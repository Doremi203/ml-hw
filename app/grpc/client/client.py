import grpc
from app.grpc.protos import ml_service_pb2, ml_service_pb2_grpc

def run():
    channel = grpc.insecure_channel("localhost:50051")
    stub = ml_service_pb2_grpc.HealthServiceStub(channel)
    response = stub.Check(ml_service_pb2.HealthRequest())
    print("Health:", response.status)

if __name__ == "__main__":
    run()