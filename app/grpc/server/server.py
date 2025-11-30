import grpc
from concurrent import futures
from app.grpc.protos import ml_service_pb2, ml_service_pb2_grpc
from app.services.datasets import list_datasets, save_dataset
from app.services.models import (
    MODEL_CLASSES,
    train_model,
    list_models,
    predict_model,
    retrain_model,
    delete_model,
)


class HealthService(ml_service_pb2_grpc.HealthServiceServicer):
    def Check(self, request, context):
        return ml_service_pb2.HealthResponse(status="ok")

class DatasetService(ml_service_pb2_grpc.DatasetServiceServicer):
    def ListDatasets(self, request, context):
        datasets = list_datasets()
        return ml_service_pb2.ListDatasetsResponse(datasets=datasets)

    def UploadDataset(self, request, context):
        from io import BytesIO

        filename = request.filename
        content = request.content

        if not (filename.endswith(".csv") or filename.endswith(".json")):
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Only CSV and JSON are allowed")

        # Create a mock file object for save_dataset function
        class MockFile:
            def __init__(self, filename, content):
                self.filename = filename
                self.file = BytesIO(content)

        mock_file = MockFile(filename, content)
        saved_filename = save_dataset(mock_file)

        return ml_service_pb2.UploadDatasetResponse(filename=saved_filename)

class ModelService(ml_service_pb2_grpc.ModelServiceServicer):

    def ListModelClasses(self, request, context):
        return ml_service_pb2.ListModelClassesResponse(
            classes=list(MODEL_CLASSES.keys())
        )

    def TrainModel(self, request, context):
        params = dict(request.params)
        try:
            model_id = train_model(
                request.model_type,
                request.dataset_name,
                request.target_column,
                params,
            )
        except Exception as e:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))

        return ml_service_pb2.TrainModelResponse(model_id=model_id)

    def ListModels(self, request, context):
        return ml_service_pb2.ListModelsResponse(
            model_ids=list_models()
        )

    def Predict(self, request, context):
        features = []
        for f in request.features:
            features.append(dict(f.values))
        try:
            preds = predict_model(request.model_id, features)
        except Exception as e:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))

        return ml_service_pb2.PredictResponse(predictions=preds)

    def Retrain(self, request, context):
        params = dict(request.params)
        try:
            retrain_model(request.model_id, params)
        except Exception as e:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        return ml_service_pb2.RetrainResponse(model_id=request.model_id)

    def DeleteModel(self, request, context):
        ok = delete_model(request.model_id)
        return ml_service_pb2.DeleteModelResponse(deleted=ok)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    ml_service_pb2_grpc.add_HealthServiceServicer_to_server(
        HealthService(),
        server
    )

    ml_service_pb2_grpc.add_DatasetServiceServicer_to_server(
        DatasetService(),
        server
    )

    ml_service_pb2_grpc.add_ModelServiceServicer_to_server(
        ModelService(), server
    )

    server.add_insecure_port("[::]:50051")
    print("gRPC server started at port 50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()