import httpx
import pytest
from types_aiobotocore_sns import SNSClient

from tomodachi_testcontainers import MotoContainer


@pytest.mark.asyncio(loop_scope="session")
async def test_moto_container_starts(moto_container: MotoContainer) -> None:
    async with httpx.AsyncClient(base_url=moto_container.get_external_url()) as client:
        response = await client.get("/moto-api/data.json")

        assert response.status_code == 200


@pytest.mark.asyncio(loop_scope="session")
async def test_create_aws_resources_andreset_moto(moto_container: MotoContainer, moto_sns_client: SNSClient) -> None:
    await moto_sns_client.create_topic(Name="test-topic")

    list_topics_response = await moto_sns_client.list_topics()
    assert list_topics_response["Topics"] == [{"TopicArn": "arn:aws:sns:us-east-1:123456789012:test-topic"}]

    moto_container.reset_moto()

    list_topics_response = await moto_sns_client.list_topics()
    assert list_topics_response["Topics"] == []
