import uuid
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from app.config import settings

_s3_client = None


def get_s3():
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client(
            "s3",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
    return _s3_client


BUCKET = settings.S3_BUCKET_NAME


def build_s3_key(firm_id: str, case_id: str, filename: str) -> str:
    date_prefix = datetime.utcnow().strftime("%Y/%m/%d")
    uid = uuid.uuid4().hex[:8]
    safe_name = filename.replace(" ", "_")
    return f"firms/{firm_id}/cases/{case_id}/{date_prefix}/{uid}_{safe_name}"


def generate_presigned_upload(
    s3_key: str,
    mime_type: str,
    expires_in: int = 900,
) -> str:
    """Return a presigned PUT URL the client uploads directly to."""
    return get_s3().generate_presigned_url(
        "put_object",
        Params={
            "Bucket": BUCKET,
            "Key": s3_key,
            "ContentType": mime_type,
        },
        ExpiresIn=expires_in,
        HttpMethod="PUT",
    )


def generate_presigned_download(s3_key: str, expires_in: int = 3600) -> str:
    """Return a presigned GET URL for a stored file."""
    return get_s3().generate_presigned_url(
        "get_object",
        Params={"Bucket": BUCKET, "Key": s3_key},
        ExpiresIn=expires_in,
    )


def upload_bytes(s3_key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
    """Directly upload bytes (used for generated audio/PDF). Returns the S3 key."""
    get_s3().put_object(
        Bucket=BUCKET,
        Key=s3_key,
        Body=data,
        ContentType=content_type,
    )
    return s3_key


def download_bytes(s3_key: str) -> bytes:
    """Download a file from S3 and return its bytes."""
    obj = get_s3().get_object(Bucket=BUCKET, Key=s3_key)
    return obj["Body"].read()


def delete_object(s3_key: str) -> None:
    try:
        get_s3().delete_object(Bucket=BUCKET, Key=s3_key)
    except ClientError:
        pass


def object_exists(s3_key: str) -> bool:
    try:
        get_s3().head_object(Bucket=BUCKET, Key=s3_key)
        return True
    except ClientError:
        return False
