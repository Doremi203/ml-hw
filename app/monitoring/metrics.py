from prometheus_client import Counter, Histogram
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI


INFERENCE_DURATION_SECONDS = Histogram(
    "ml_inference_duration_seconds",
    "Model inference duration in seconds",
    labelnames=("status",),
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

INFERENCE_REQUESTS_TOTAL = Counter(
    "ml_inference_requests_total",
    "Total number of inference requests",
    labelnames=("status",),
)


def setup_metrics(app: FastAPI) -> None:
    """Attach default HTTP metrics and expose /metrics endpoint."""
    instrumentator = Instrumentator(excluded_handlers=["/metrics"])
    instrumentator.instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)


def observe_inference(duration_seconds: float, status: str) -> None:
    """Track inference latency and success/error counters."""
    INFERENCE_DURATION_SECONDS.labels(status=status).observe(duration_seconds)
    INFERENCE_REQUESTS_TOTAL.labels(status=status).inc()

