from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import asyncio
import aiohttp
import time
from pathlib import Path
from app.logging.logging import logger
from app.services.datasets import get_s3_client
from app.services.models import MODELS_DIR, list_models

router = APIRouter()


class HealthCheckResult:
    def __init__(self, service: str, status: str, details: Dict[str, Any] = None):
        self.service = service
        self.status = status
        self.details = details or {}
        self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "service": self.service,
            "status": self.status,
            "details": self.details,
            "timestamp": self.timestamp
        }


async def check_s3_connection() -> HealthCheckResult:
    """Check S3/MinIO connection"""
    try:
        s3_client = get_s3_client()
        # Test connection by listing buckets
        s3_client.list_buckets()
        return HealthCheckResult("s3", "healthy", {"endpoint": s3_client._endpoint.host})
    except Exception as e:
        logger.error(f"S3 healthcheck failed: {e}")
        return HealthCheckResult("s3", "unhealthy", {"error": str(e)})


async def check_models_directory() -> HealthCheckResult:
    """Check models directory and available models"""
    try:
        if not MODELS_DIR.exists():
            return HealthCheckResult("models", "unhealthy", {"error": "Models directory does not exist"})
        
        models = list_models()
        return HealthCheckResult("models", "healthy", {
            "models_directory": str(MODELS_DIR),
            "available_models": len(models),
            "model_ids": models
        })
    except Exception as e:
        logger.error(f"Models healthcheck failed: {e}")
        return HealthCheckResult("models", "unhealthy", {"error": str(e)})


async def check_minio_health() -> HealthCheckResult:
    """Check MinIO health endpoint"""
    try:
        s3_client = get_s3_client()
        endpoint_url = s3_client._endpoint.host
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{endpoint_url}/minio/health/live") as response:
                if response.status == 200:
                    return HealthCheckResult("minio", "healthy", {"endpoint": endpoint_url})
                else:
                    return HealthCheckResult("minio", "unhealthy", {"status_code": response.status})
    except Exception as e:
        logger.error(f"MinIO healthcheck failed: {e}")
        return HealthCheckResult("minio", "unhealthy", {"error": str(e)})


@router.get("/health")
async def health_check():
    """Comprehensive health check of all services"""
    logger.info("Performing comprehensive health check")
    
    # Run all checks concurrently
    checks = [
        check_s3_connection(),
        check_models_directory(),
        check_minio_health()
    ]
    
    results = await asyncio.gather(*checks, return_exceptions=True)
    
    # Process results
    overall_status = "healthy"
    service_results = {}
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            service_name = ["s3", "models", "minio"][i]
            service_results[service_name] = HealthCheckResult(
                service_name, "unhealthy", {"error": str(result)}
            ).to_dict()
            overall_status = "unhealthy"
        else:
            service_results[result.service] = result.to_dict()
            if result.status != "healthy":
                overall_status = "degraded"
    
    response = {
        "status": overall_status,
        "timestamp": time.time(),
        "services": service_results,
        "version": "1.0.0"
    }
    
    logger.info(f"Health check completed: {overall_status}")
    return response


@router.get("/healthz")
async def healthz_check():
    """Simple liveness/readiness check"""
    logger.info("Performing healthz check")
    
    # Quick basic checks
    try:
        # Check models directory
        if not MODELS_DIR.exists():
            raise HTTPException(status_code=503, detail="Models directory not available")
        
        # Check S3 connection
        s3_client = get_s3_client()
        s3_client.list_buckets()
        
        logger.info("Healthz check passed")
        return {"status": "ok", "timestamp": time.time()}
        
    except Exception as e:
        logger.error(f"Healthz check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")


@router.get("/health/services/{service_name}")
async def specific_service_health(service_name: str):
    """Health check for a specific service"""
    logger.info(f"Performing health check for service: {service_name}")
    
    if service_name == "s3":
        result = await check_s3_connection()
    elif service_name == "models":
        result = await check_models_directory()
    elif service_name == "minio":
        result = await check_minio_health()
    else:
        raise HTTPException(status_code=404, detail="Service not found")
    
    if result.status != "healthy":
        raise HTTPException(status_code=503, detail=f"{service_name} service is unhealthy")
    
    return result.to_dict()