import httpx
import pytest
from types_aiobotocore_sns import SNSClient

from tomodachi_testcontainers import LocalStackContainer


@pytest.mark.asyncio()
async def test_localstack_container_starts(localstack_container: LocalStackContainer) -> None:
    async with httpx.AsyncClient(base_url=localstack_container.get_external_url()) as client:
        response = await client.get("_localstack/health")

        assert response.status_code == 200


@pytest.mark.asyncio()
async def test_create_aws_resources_and_restart_localstack_container(
    localstack_container: LocalStackContainer, localstack_sns_client: SNSClient
) -> None:
    await localstack_sns_client.create_topic(Name="test-topic")

    list_topics_response = await localstack_sns_client.list_topics()
    assert list_topics_response["Topics"] == [{"TopicArn": "arn:aws:sns:us-east-1:000000000000:test-topic"}]

    localstack_container.restart()

    list_topics_response = await localstack_sns_client.list_topics()
    assert list_topics_response["Topics"] == []
