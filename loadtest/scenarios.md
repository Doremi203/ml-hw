# Load testing scenarios

## Goal

Validate service behavior under inference load and collect key metrics:

- RPS by endpoint
- Latency p50/p95/p99
- Error rate (4xx/5xx)
- Inference duration p50/p95

## Scenario 1 - Baseline (steady load)

- 20 users, spawn rate 5 users/sec
- Duration: 10 minutes
- Mix:
  - 70% `POST /models/{model_id}/predict`
  - 20% `GET /healthz`
  - 10% `GET /models/`
- Purpose: capture stable baseline for p50/p95 and RPS.

## Scenario 2 - Stress ramp-up

- Start from 20 users, increase to 200 users in steps of 20 every 2 minutes
- Duration: 20 minutes
- Same endpoint mix as baseline
- Purpose: find saturation point where p95 latency and error rate start growing sharply.

## Scenario 3 - Spike resilience

- Warmup: 30 users for 5 minutes
- Spike: 300 users for 2 minutes
- Recovery: 30 users for 8 minutes
- Purpose: evaluate short burst handling and recovery time.

## Acceptance criteria (initial)

- Error rate < 1% during baseline
- p95 HTTP latency for predict endpoint < 500ms during baseline
- p95 inference time < 400ms during baseline

## PromQL queries

### RPS by endpoint

```promql
sum(rate(http_requests_total{job="ml-rest"}[1m])) by (handler, method)
```

### HTTP latency p50/p95/p99

```promql
histogram_quantile(0.50, sum(rate(http_request_duration_seconds_bucket{job="ml-rest"}[5m])) by (le, handler))
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{job="ml-rest"}[5m])) by (le, handler))
histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{job="ml-rest"}[5m])) by (le, handler))
```

### Error rate (4xx+5xx)

```promql
100 * sum(rate(http_requests_total{job="ml-rest",status=~"4..|5.."}[5m])) by (handler)
  / clamp_min(sum(rate(http_requests_total{job="ml-rest"}[5m])) by (handler), 1e-9)
```

### Inference duration p50/p95

```promql
histogram_quantile(0.50, sum(rate(ml_inference_duration_seconds_bucket{status="success"}[5m])) by (le))
histogram_quantile(0.95, sum(rate(ml_inference_duration_seconds_bucket{status="success"}[5m])) by (le))
```

