from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.datasets import save_dataset, list_datasets
from app.logging.logging import logger

router = APIRouter(prefix="/datasets")


@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    logger.info(f"Uploading dataset: {file.filename}")

    if not (file.filename.endswith(".csv") or file.filename.endswith(".json")):
        raise HTTPException(status_code=400, detail="Only CSV or JSON allowed")

    filename = save_dataset(file)
    return {"filename": filename}


@router.get("/")
async def get_datasets():
    datasets = list_datasets()
    logger.info("Listing datasets")
    return {"datasets": datasets}