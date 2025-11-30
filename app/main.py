from fastapi import FastAPI
from app.logging.logging import logger
from app.api.datasets import router as datasets_router
from app.api.models import router as models_router

app = FastAPI(title="ML service")

app.include_router(datasets_router)
app.include_router(models_router)

@app.get("/health")
def health_check():
    logger.info("Health check")
    return {"status": "ok"}
