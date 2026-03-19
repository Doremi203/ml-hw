# ML Service API Documentation

## Overview

The ML Service provides a RESTful API for machine learning operations, including dataset management, model training, prediction, and comprehensive health monitoring. The service is built with FastAPI and includes gRPC support for high-performance operations.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible.

## API Endpoints

### Healthcheck Endpoints

#### GET /metrics

Prometheus metrics endpoint for scraping service and inference metrics.

**Examples of exported series:**

- `http_requests_total`
- `http_request_duration_seconds_bucket`
- `ml_inference_duration_seconds_bucket`
- `ml_inference_requests_total`

**Status Codes:**

- `200 OK` - Metrics exported successfully

#### GET /health

Comprehensive health check of all services.

**Response:**

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
        "models_directory": "/app/data/models",
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

**Status Codes:**

- `200 OK` - Service is healthy
- `503 Service Unavailable` - Service is unhealthy

#### GET /healthz

Simple liveness/readiness check.

**Response:**

```json
{
  "status": "ok",
  "timestamp": 1645678901.234
}
```

**Status Codes:**

- `200 OK` - Service is ready
- `503 Service Unavailable` - Service is not ready

#### GET /health/services/{service_name}

Health check for a specific service.

**Path Parameters:**

- `service_name` (string, required): Service name - `s3`, `models`, or `minio`

**Response:**

```json
{
  "service": "s3",
  "status": "healthy",
  "details": { "endpoint": "http://localhost:9000" },
  "timestamp": 1645678901.234
}
```

**Status Codes:**

- `200 OK` - Service is healthy
- `404 Not Found` - Service not found
- `503 Service Unavailable` - Service is unhealthy

---

### Dataset Endpoints

#### POST /datasets/upload

Upload a dataset file (CSV or JSON format).

**Request:**

- Method: POST
- Content-Type: multipart/form-data
- Body: File upload

**Response:**

```json
{
  "filename": "dataset.csv"
}
```

**Status Codes:**

- `200 OK` - File uploaded successfully
- `400 Bad Request` - Invalid file format
- `500 Internal Server Error` - Upload failed

#### GET /datasets/

List all available datasets.

**Response:**

```json
{
  "datasets": ["dataset1.csv", "dataset2.json"]
}
```

**Status Codes:**

- `200 OK` - Successfully retrieved dataset list

---

### Model Endpoints

#### GET /models/classes

Get available model classes.

**Response:**

```json
{
  "available_models": ["logistic_regression", "random_forest"]
}
```

**Status Codes:**

- `200 OK` - Successfully retrieved model classes

#### POST /models/train

Train a new model.

**Request Body:**

```json
{
  "model_type": "logistic_regression",
  "dataset_name": "dataset.csv",
  "target_column": "target",
  "params": {
    "C": 1.0,
    "max_iter": 1000
  }
}
```

**Response:**

```json
{
  "model_id": "ea22fde4-8531-4d79-b523-7514ccbbbab3"
}
```

**Status Codes:**

- `200 OK` - Model training started successfully
- `400 Bad Request` - Invalid model type or parameters
- `500 Internal Server Error` - Training failed

#### GET /models/

List all available models.

**Response:**

```json
{
  "models": ["ea22fde4-8531-4d79-b523-7514ccbbbab3"]
}
```

**Status Codes:**

- `200 OK` - Successfully retrieved model list

#### POST /models/{model_id}/predict

Make predictions using a trained model.

**Path Parameters:**

- `model_id` (string, required): Model identifier

**Request Body:**

```json
{
  "features": [
    { "feature1": 1.0, "feature2": 2.0 },
    { "feature1": 3.0, "feature2": 4.0 }
  ]
}
```

**Response:**

```json
{
  "predictions": [0, 1]
}
```

**Status Codes:**

- `200 OK` - Predictions generated successfully
- `400 Bad Request` - Invalid features or model not found
- `500 Internal Server Error` - Prediction failed

#### POST /models/{model_id}/retrain

Retrain an existing model with new parameters.

**Path Parameters:**

- `model_id` (string, required): Model identifier

**Request Body:**

```json
{
  "params": {
    "C": 2.0,
    "max_iter": 2000
  }
}
```

**Response:**

```json
{
  "model_id": "ea22fde4-8531-4d79-b523-7514ccbbbab3"
}
```

**Status Codes:**

- `200 OK` - Model retrained successfully
- `400 Bad Request` - Invalid parameters or model not found
- `500 Internal Server Error` - Retraining failed

#### DELETE /models/{model_id}

Delete a model.

**Path Parameters:**

- `model_id` (string, required): Model identifier

**Response:**

```json
{
  "status": "deleted"
}
```

**Status Codes:**

- `200 OK` - Model deleted successfully
- `404 Not Found` - Model not found

---

## Error Responses

All endpoints return appropriate HTTP status codes and error messages:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common status codes:

- `200 OK` - Request successful
- `400 Bad Request` - Invalid request parameters
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server-side error
- `503 Service Unavailable` - Service not ready

---

## Data Models

### TrainRequest

```json
{
  "model_type": "string",
  "dataset_name": "string",
  "target_column": "string",
  "params": "object"
}
```

### PredictRequest

```json
{
  "features": "array of objects"
}
```

### RetrainRequest

```json
{
  "params": "object"
}
```

---

## gRPC API

The service also provides a gRPC API for high-performance operations:

### Service Definition

- Package: `mlservice`
- Service: `MLService`

### Available Methods

- `TrainModel` - Train a new model
- `Predict` - Make predictions
- `RetrainModel` - Retrain existing model
- `ListModels` - List available models
- `GetModelClasses` - Get available model classes

### gRPC Endpoint

```
localhost:50051
```

---

## Healthcheck Integration

The service includes comprehensive healthcheck monitoring:

### Docker Healthcheck

The ml-api container includes a healthcheck that:

- Tests the `/healthz` endpoint every 30 seconds
- Has a 10-second timeout
- Retries 3 times
- Includes a 40-second start period

### Service Dependencies

- **S3/MinIO**: Storage connectivity
- **Models Directory**: Model file availability
- **External Services**: Health endpoint monitoring

---

## Testing

### API Testing

Use the provided `test_main.http` file for testing endpoints:

```bash
# Install httpie if not already installed
pip install httpie

# Run tests
http :8000/health
http :8000/healthz
http :8000/health/services/s3
http :8000/health/services/models
http :8000/health/services/minio
```

### Integration Testing

The service can be tested with Docker Compose:

```bash
docker-compose up -d
docker-compose ps  # Check service health
docker-compose logs ml-api  # View logs
```

---

## Rate Limiting

Currently, the API does not implement rate limiting. Consider adding rate limiting for production use.

## CORS

The API includes CORS headers and is accessible from web browsers.

## OpenAPI Documentation

Interactive API documentation is available at:

```
http://localhost:8000/docs
```

For alternative documentation format:

```
http://localhost:8000/redoc
```

---

## Examples

### Train a Model

```bash
curl -X POST "http://localhost:8000/models/train" \
     -H "Content-Type: application/json" \
     -d '{
       "model_type": "logistic_regression",
       "dataset_name": "dataset.csv",
       "target_column": "target",
       "params": {"C": 1.0}
     }'
```

### Make Predictions

```bash
curl -X POST "http://localhost:8000/models/ea22fde4-8531-4d79-b523-7514ccbbbab3/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "features": [
         {"feature1": 1.0, "feature2": 2.0},
         {"feature1": 3.0, "feature2": 4.0}
       ]
     }'
```

### Check Health

```bash
curl -X GET "http://localhost:8000/health"
```

---

## Monitoring

### Logging

All API operations are logged to:

- Console output
- `logs/service.log` file (with 10MB rotation, 10-day retention)

### Healthcheck Monitoring

- Service health is logged for all healthcheck requests
- Individual service status is tracked and reported
- Docker healthcheck status available via `docker-compose ps`

---

## Deployment

### Docker

```bash
docker-compose up -d
```

### Kubernetes

See `k8s/` directory for Kubernetes deployment manifests.

### Environment Variables

Key environment variables:

- `S3_BUCKET`: Storage bucket name
- `S3_ENDPOINT_URL`: MinIO/S3 endpoint URL
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_REGION`: AWS region

---

## Support

For issues and feature requests, please check the project documentation or create an issue in the project repository.
