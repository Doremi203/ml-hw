# Locust load testing

## Prerequisites

- Service is running and reachable at `http://localhost:8000`
- At least one trained model ID for inference tests

## Run

```bash
export MODEL_ID="<your-model-id>"
export PREDICT_PAYLOAD='{"features":[{"feature1":1.0,"feature2":2.0}]}'
locust -f loadtest/locustfile.py --host http://localhost:8000
```

Open Locust UI at `http://localhost:8089` and run scenarios from `loadtest/scenarios.md`.

## Headless example

```bash
locust -f loadtest/locustfile.py \
  --host http://localhost:8000 \
  --headless \
  -u 20 \
  -r 5 \
  -t 10m
```

