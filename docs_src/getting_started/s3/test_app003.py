import httpx
import pytest
from types_aiobotocore_s3 import S3Client


@pytest.mark.asyncio(loop_scope="session")
async def test_save_and_get_file(http_client: httpx.AsyncClient, localstack_s3_client: S3Client) -> None:
    await localstack_s3_client.create_bucket(Bucket="autotest-my-bucket")

    response = await http_client.post("/file/", json={"filename": "test.txt", "content": "Hello, world!"})
    assert response.status_code == 200
    assert response.json() == {"key": "test.txt"}

    # Testing on the same level of abstraction and not exposing application's internal implementation details
    response = await http_client.get("/file/test.txt")
    assert response.status_code == 200
    assert response.json() == {"content": "Hello, world!"}
