from pathlib import Path
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import joblib
import uuid
from app.services.datasets import get_dataset
from clearml import Task, OutputModel

MODELS_DIR = Path(__file__).resolve().parents[2] / "data" / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)


MODEL_CLASSES = {
    "logistic_regression": LogisticRegression,
    "random_forest": RandomForestClassifier,
}


def load_dataset(name: str) -> pd.DataFrame:
    """Загружает датасет из S3."""
    from io import BytesIO

    data = get_dataset(name)
    if name.endswith(".csv"):
        return pd.read_csv(BytesIO(data))
    elif name.endswith(".json"):
        return pd.read_json(BytesIO(data))
    else:
        raise ValueError("Unsupported format")


def train_model(model_type: str, dataset_name: str, target_column: str, params: dict):
    """Обучает модель и сохраняет её на диск."""
    if model_type not in MODEL_CLASSES:
        raise ValueError("Unknown model type")

    df = load_dataset(dataset_name)

    task = Task.init(
        project_name="ML Service",
        task_name=f"Train {model_type}",
        tags=["training"]
    )

    task.connect(params)
    task.connect({"dataset": dataset_name})

    X = df.drop(columns=[target_column])
    y = df[target_column]

    model_class = MODEL_CLASSES[model_type]
    params = convert_params(params)
    model = model_class(**params)
    model.fit(X, y)

    model_id = str(uuid.uuid4())
    model_path = MODELS_DIR / f"{model_id}.joblib"

    joblib.dump({
        "model": model,
        "model_type": model_type,
        "dataset": dataset_name,
        "target": target_column,
        "params": params,
        "features": list(X.columns),
    }, model_path)

    output_model = OutputModel(task=task, name=model_type)
    output_model.update_weights(
        weights_filename=str(model_path)
    )
    output_model.update_design(dataset_name, params)

    task.mark_completed()

    return model_id

def convert_params(params: dict) -> dict:
    """Преобразует строковые параметры из gRPC в корректные типы."""
    converted = {}
    for key, value in params.items():
        try:
            converted[key] = int(value)
            continue
        except ValueError:
            pass

        try:
            converted[key] = float(value)
            continue
        except ValueError:
            pass

        if value.lower() in ("true", "false"):
            converted[key] = value.lower() == "true"
            continue

        converted[key] = value

    return converted

def list_models() -> list[str]:
    """Возвращает список ID моделей."""
    return [p.stem for p in MODELS_DIR.iterdir() if p.is_file()]

def load_model(model_id: str):
    """Загружает модель из файла."""
    path = MODELS_DIR / f"{model_id}.joblib"
    if not path.exists():
        raise ValueError("Model not found")

    data = joblib.load(path)
    return data, path


def predict_model(model_id: str, features: list[dict]):
    """Делает предсказание по модели."""
    data, _ = load_model(model_id)
    model = data["model"]
    feature_order = data["features"]

    # Преобразуем список dict → DataFrame c правильным порядком колонок
    df = pd.DataFrame(features)[feature_order]

    preds = model.predict(df)
    return preds.tolist()


def retrain_model(model_id: str, params: dict):
    """Переобучение модели с новыми гиперпараметрами."""
    data, path = load_model(model_id)
    df = load_dataset(data["dataset"])

    task = Task.init(
        project_name="ML Service",
        task_name=f"Retrain {model_id}",
        tags=["retrain"]
    )

    task.connect(params)

    X = df.drop(columns=[data["target"]])
    y = df[data["target"]]

    model_class = MODEL_CLASSES[data["model_type"]]
    new_model = model_class(**params)
    new_model.fit(X, y)

    data["model"] = new_model
    data["params"] = params

    joblib.dump(data, path)

    output_model = OutputModel(task=task, name=f"retrained-{model_id}")
    output_model.update_weights(str(path))
    task.mark_completed()

    return model_id


def delete_model(model_id: str):
    """Удаление файла модели."""
    path = MODELS_DIR / f"{model_id}.joblib"
    if path.exists():
        path.unlink()
        return True
    return False