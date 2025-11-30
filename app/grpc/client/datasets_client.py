import grpc
from app.grpc.protos import ml_service_pb2, ml_service_pb2_grpc


def list_datasets():
    channel = grpc.insecure_channel("localhost:50051")
    stub = ml_service_pb2_grpc.DatasetServiceStub(channel)
    resp = stub.ListDatasets(ml_service_pb2.ListDatasetsRequest())
    print("Datasets:", resp.datasets)


def upload_dataset(path):
    filename = path.split("/")[-1]
    with open(path, "rb") as f:
        content = f.read()

    channel = grpc.insecure_channel("localhost:50051")
    stub = ml_service_pb2_grpc.DatasetServiceStub(channel)

    request = ml_service_pb2.UploadDatasetRequest(
        filename=filename,
        content=content
    )

    resp = stub.UploadDataset(request)
    print("Uploaded:", resp.filename)


if __name__ == "__main__":
    list_datasets()
    upload_dataset("test.csv")  # пример
    list_datasets()