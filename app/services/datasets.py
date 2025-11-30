import os
import boto3
from botocore.exceptions import ClientError
from pathlib import Path

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).resolve().parents[2] / ".env"
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    # dotenv not available, skip
    pass

# S3 configuration
S3_BUCKET = os.getenv("S3_BUCKET", "ml-datasets-bucket")
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")  # For MinIO or other S3-compatible services
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Initialize S3 client
def get_s3_client():
    return boto3.client(
        's3',
        endpoint_url=S3_ENDPOINT_URL,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )


def save_dataset(file) -> str:
    """Save dataset file to S3 bucket"""
    filename = file.filename
    s3_client = get_s3_client()

    try:
        # Upload file to S3
        file_content = file.file.read()
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=f"datasets/{filename}",
            Body=file_content
        )

        # Reset file pointer for potential reuse
        file.file.seek(0)

        return filename
    except ClientError as e:
        raise Exception(f"Failed to upload dataset to S3: {e}")


def list_datasets() -> list[str]:
    """List all datasets stored in S3 bucket"""
    s3_client = get_s3_client()

    try:
        response = s3_client.list_objects_v2(
            Bucket=S3_BUCKET,
            Prefix="datasets/"
        )

        if 'Contents' not in response:
            return []

        return [
            obj['Key'].replace('datasets/', '')
            for obj in response['Contents']
            if not obj['Key'].endswith('/')  # Skip directories
        ]
    except ClientError as e:
        raise Exception(f"Failed to list datasets from S3: {e}")


def get_dataset(filename: str) -> bytes:
    """Download dataset file from S3 bucket"""
    s3_client = get_s3_client()

    try:
        response = s3_client.get_object(
            Bucket=S3_BUCKET,
            Key=f"datasets/{filename}"
        )
        return response['Body'].read()
    except ClientError as e:
        raise Exception(f"Failed to download dataset from S3: {e}")


def delete_dataset(filename: str) -> bool:
    """Delete dataset file from S3 bucket"""
    s3_client = get_s3_client()

    try:
        s3_client.delete_object(
            Bucket=S3_BUCKET,
            Key=f"datasets/{filename}"
        )
        return True
    except ClientError as e:
        raise Exception(f"Failed to delete dataset from S3: {e}")
