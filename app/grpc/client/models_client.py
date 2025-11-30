import grpc
from app.grpc.protos import ml_service_pb2, ml_service_pb2_grpc


def test_list_classes():
    channel = grpc.insecure_channel("localhost:50051")
    stub = ml_service_pb2_grpc.ModelServiceStub(channel)
    resp = stub.ListModelClasses(ml_service_pb2.ListModelClassesRequest())
    print("Available:", resp.classes)


def test_train():
    channel = grpc.insecure_channel("localhost:50051")
    stub = ml_service_pb2_grpc.ModelServiceStub(channel)

    resp = stub.TrainModel(ml_service_pb2.TrainModelRequest(
        model_type="logistic_regression",
        dataset_name="test.csv",
        target_column="c1",
        params={"max_iter": "200"}
    ))

    print("Model ID:", resp.model_id)


def test_predict(model_id):
    channel = grpc.insecure_channel("localhost:50051")
    stub = ml_service_pb2_grpc.ModelServiceStub(channel)

    req = ml_service_pb2.PredictRequest(
        model_id=model_id,
        features=[
            ml_service_pb2.Feature(values={"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2})
        ]
    )

    resp = stub.Predict(req)
    print("Pred:", resp.predictions)


if __name__ == "__main__":
    test_list_classes()
    test_train()