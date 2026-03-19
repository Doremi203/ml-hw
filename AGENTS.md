# ML Homework Agents Documentation

## Overview
This project contains multiple agents working together to provide a machine learning service with gRPC API, data processing, and deployment capabilities. The agents are organized into the following categories:

## Core Agents

### 1. Data Ingestion Agent
- **Location**: `data/datasets/` and `data/models/`
- **Responsibilities**:
  - Manages dataset storage and versioning via DVC
  - Handles model artifact storage (e.g., joblib files)
  - Integrates with Docker-based data processing pipelines

### 2. Model Training Agent
- **Location**: `app/services/models.py`
- **Responsibilities**:
  - Executes ML training workflows
  - Integrates with gRPC model service
  - Manages model versioning and deployment

### 3. gRPC Service Agent
- **Location**: `app/grpc/server/server.py`
- **Responsibilities**:
  - Provides REST/gRPC API for model inference
  - Communicates with Dockerized ML services
  - Supports model version routing

## Deployment Agents

### 1. Docker Compose Agent
- **Location**: `docker-compose.yaml`
- **Responsibilities**:
  - Orchestrates containerized services:
    - ML model server
    - Data processing workers
    - Dashboard frontend

### 2. Kubernetes Agent
- **Location**: `k8s/` directory
- **Responsibilities**:
  - Manages cloud-native deployment:
    - MinIO storage integration
    - Horizontal scaling for model inference
    - Service mesh configuration

## Monitoring Agent
- **Location**: `logs/service.log`, `app/monitoring/metrics.py`, `k8s/monitoring.yaml`
- **Responsibilities**:
  - Aggregates system metrics
  - Tracks API request patterns
  - Provides observability for distributed services
  - Exposes Prometheus-compatible `/metrics` endpoint
  - Integrates VictoriaMetrics + Grafana dashboards

## Development Agents

### 1. Environment Setup Agent
- **Location**: `.env` file
- **Responsibilities**:
  - Manages environment variables for:
    - Docker containerization
    - gRPC service configuration
    - Kubernetes deployment parameters

### 2. Testing Agent
- **Location**: `test_main.http`, `test.csv`, `loadtest/locustfile.py`, `loadtest/scenarios.md`
- **Responsibilities**:
  - Provides API testing interface
  - Contains sample datasets for validation
  - Runs load testing scenarios and captures performance baselines

## Architecture Diagram
```
[Data Sources] --> [Data Ingestion Agent] --> [Model Training Agent]
                             |                           |
                             v                           v
                   [gRPC Service Agent] --> [Dashboard Agent]
                             |
                   [Kubernetes Agent]
```

## Contribution Guidelines
1. Always update the AGENTS.md file when adding new components
2. Use the DVC system for versioned data management
3. Follow the Docker/Kubernetes deployment patterns
4. Maintain consistent gRPC API versioning

For more details on specific agents, refer to their respective implementation files in the project structure.