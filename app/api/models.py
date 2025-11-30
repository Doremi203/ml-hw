from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.logging.logging import logger
from app.services.models import (
    MODEL_CLASSES,
    train_model,
    list_models,
    predict_model,
    retrain_model,
    delete_model,
)


router = APIRouter(prefix="/models")


class TrainRequest(BaseModel):
    model_type: str
    dataset_name: str
    target_column: str
    params: dict = {}


@router.get("/classes")
def get_model_classes():
    """Какие модели доступны."""
    return {"available_models": list(MODEL_CLASSES.keys())}


@router.post("/train")
def train(req: TrainRequest):
    logger.info(f"Training model: {req.model_type}")

    try:
        model_id = train_model(
            req.model_type,
            req.dataset_name,
            req.target_column,
            req.params,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"model_id": model_id}


@router.get("/")
def models_list():
    return {"models": list_models()}

class PredictRequest(BaseModel):
    features: list[dict]   # список объектов для предсказаний


@router.post("/{model_id}/predict")
def predict(model_id: str, req: PredictRequest):
    logger.info(f"Predicting with model {model_id}")

    try:
        preds = predict_model(model_id, req.features)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"predictions": preds}

class RetrainRequest(BaseModel):
    params: dict = {}


@router.post("/{model_id}/retrain")
def retrain(model_id: str, req: RetrainRequest):
    logger.info(f"Retraining model {model_id}")

    try:
        mid = retrain_model(model_id, req.params)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"model_id": mid}


@router.delete("/{model_id}")
def delete(model_id: str):
    logger.info(f"Deleting model {model_id}")

    if delete_model(model_id):
        return {"status": "deleted"}

    raise HTTPException(status_code=404, detail="Model not found")