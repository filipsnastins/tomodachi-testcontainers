import uuid

import httpx
import pytest
from types_aiobotocore_s3 import S3Client

from tomodachi_testcontainers import MinioContainer


@pytest.mark.asyncio(loop_scope="session")
async def test_minio_container_starts(minio_container: MinioContainer) -> None:
    async with httpx.AsyncClient(base_url=minio_container.get_external_url()) as client:
        response = await client.get("/minio/health/live")

        assert response.status_code == 200


@pytest.mark.asyncio(loop_scope="session")
async def test_minio_s3_client(minio_s3_client: S3Client) -> None:
    bucket = f"bucket-{uuid.uuid4()}"
    filename = f"{uuid.uuid4()}.txt"
    await minio_s3_client.create_bucket(Bucket=bucket)

    await minio_s3_client.put_object(Bucket=bucket, Key=filename, Body=b"Hello, World!")

    get_object_response = await minio_s3_client.get_object(Bucket=bucket, Key=filename)
    body = await get_object_response["Body"].read()
    assert body == b"Hello, World!"


@pytest.mark.asyncio(loop_scope="session")
async def test_reset_minio(minio_container: MinioContainer, minio_s3_client: S3Client) -> None:
    bucket = f"bucket-{uuid.uuid4()}"
    await minio_s3_client.create_bucket(Bucket=bucket)

    minio_container.reset_minio()

    list_buckets_response = await minio_s3_client.list_buckets()
    assert len(list_buckets_response["Buckets"]) == 0
