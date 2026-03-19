from fastapi import FastAPI
from app.api.datasets import router as datasets_router
from app.api.models import router as models_router
from app.api.health import router as health_router
from app.monitoring.metrics import setup_metrics

app = FastAPI(title="ML service")

app.include_router(datasets_router)
app.include_router(models_router)
app.include_router(health_router)

setup_metrics(app)

