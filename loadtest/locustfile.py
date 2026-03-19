import json
import os

from locust import HttpUser, between, task


MODEL_ID = os.getenv("MODEL_ID", "")
PREDICT_PAYLOAD_RAW = os.getenv("PREDICT_PAYLOAD", '{"features": []}')

try:
    PREDICT_PAYLOAD = json.loads(PREDICT_PAYLOAD_RAW)
except json.JSONDecodeError:
    PREDICT_PAYLOAD = {"features": []}


class MLServiceUser(HttpUser):
    wait_time = between(0.1, 0.8)

    @task(1)
    def healthz(self):
        self.client.get("/healthz", name="/healthz")

    @task(1)
    def list_models(self):
        self.client.get("/models/", name="/models/")

    @task(4)
    def predict(self):
        if not MODEL_ID or not PREDICT_PAYLOAD.get("features"):
            return

        endpoint = f"/models/{MODEL_ID}/predict"
        with self.client.post(
            endpoint,
            json=PREDICT_PAYLOAD,
            name="/models/{model_id}/predict",
            catch_response=True,
        ) as response:
            if response.status_code >= 500:
                response.failure("Server error during inference")

