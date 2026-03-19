# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Healthcheck feature implementation with comprehensive service monitoring
- Prometheus-compatible `/metrics` endpoint in FastAPI service
- HTTP and inference latency metrics for percentile tracking (p50/p95/p99)
- Kubernetes monitoring stack in `k8s/monitoring.yaml`:
  - VictoriaMetrics
  - vmagent scraping `ml-rest`
  - Grafana with pre-provisioned datasource and dashboard
- Locust-based load-testing suite in `loadtest/` with documented scenarios

## [1.1.0] - 2026-02-22

### Added

- **Healthcheck API Module** (`app/api/health.py`)
  - `/health` - Comprehensive health check of all services
  - `/healthz` - Simple liveness/readiness check
  - `/health/services/{service_name}` - Individual service health checks
  - Support for S3/MinIO connection monitoring
  - Model directory and availability verification
  - Async health checks with concurrent service validation

- **Service Monitoring**
  - S3/MinIO connectivity verification
  - Models directory health checks
  - External service endpoint monitoring
  - Timeout handling and error reporting

- **Docker Integration**
  - Healthcheck configuration in `docker-compose.yaml`
  - Container health monitoring for ml-api service
  - Proper start period and retry configuration

- **Testing Infrastructure**
  - Comprehensive test cases in `test_main.http`
  - Tests for all healthcheck endpoints
  - Individual service health validation

- **Dependencies**
  - Added `aiohttp` for async HTTP requests
  - Enhanced error handling and logging

### Changed

- **Main Application** (`app/main.py`)
  - Removed basic health endpoint
  - Integrated comprehensive healthcheck router
  - Enhanced logging integration

- **Requirements** (`requirements.txt`)
  - Added `aiohttp` dependency for async health checks

### Technical Details

- **Healthcheck Endpoints:**
  - `GET /health` - Returns overall status and individual service health
  - `GET /healthz` - Simple readiness check (returns 200 OK or 503)
  - `GET /health/services/{service_name}` - Check specific service (s3, models, minio)

- **Service Validation:**
  - S3: Tests bucket listing and connection
  - Models: Validates directory existence and model availability
  - MinIO: Checks health endpoint availability

- **Response Format:**

  ```json
  {
    "status": "healthy|degraded|unhealthy",
    "timestamp": 1645678901.234,
    "services": {
      "s3": {
        "service": "s3",
        "status": "healthy",
        "details": { "endpoint": "http://localhost:9000" },
        "timestamp": 1645678901.234
      },
      "models": {
        "service": "models",
        "status": "healthy",
        "details": {
          "models_directory": "/path/to/models",
          "available_models": 1,
          "model_ids": ["model-id-123"]
        },
        "timestamp": 1645678901.234
      },
      "minio": {
        "service": "minio",
        "status": "healthy",
        "details": { "endpoint": "http://localhost:9000" },
        "timestamp": 1645678901.234
      }
    },
    "version": "1.0.0"
  }
  ```

- **Docker Healthcheck:**
  - Tests `/healthz` endpoint every 30 seconds
  - 10-second timeout with 3 retries
  - 40-second start period for container initialization

### Security

- No breaking changes to existing API
- Backward compatible with existing endpoints
- Proper error handling without exposing sensitive information

### Testing

- All healthcheck endpoints tested via `test_main.http`
- Integration with existing test suite
- Container health monitoring validation

## [1.0.0] - 2026-02-21

### Added

- Initial ML service implementation
- FastAPI application with datasets and models endpoints
- gRPC service integration
- Docker containerization
- MinIO storage integration
- Streamlit dashboard
- Basic logging system
