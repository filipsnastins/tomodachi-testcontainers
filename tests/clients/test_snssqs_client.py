from typing import Dict

import pytest
from tomodachi.envelope.json_base import JsonBase
from tomodachi.envelope.protobuf_base import ProtobufBase
from types_aiobotocore_sns import SNSClient
from types_aiobotocore_sqs import SQSClient

from tests.proto_build.message_pb2 import Person
from tomodachi_testcontainers.clients import snssqs_client

pytestmark = pytest.mark.usefixtures("_reset_moto_container_on_teardown")


@pytest.mark.asyncio()
async def test_publish_fails_if_topic_does_not_exist(moto_sns_client: SNSClient) -> None:
    with pytest.raises(ValueError, match="Topic does not exist: test-topic"):
        await snssqs_client.publish(moto_sns_client, "test-topic", {"message": "1"}, JsonBase)


@pytest.mark.asyncio()
async def test_no_messages_received(moto_sns_client: SNSClient, moto_sqs_client: SQSClient) -> None:
    await snssqs_client.subscribe_to(moto_sns_client, moto_sqs_client, topic="test-topic", queue="test-queue")

    messages = await snssqs_client.receive(moto_sqs_client, "test-queue", JsonBase, Dict[str, str])

    assert messages == []


@pytest.mark.asyncio()
async def test_publish_and_receive_messages(moto_sns_client: SNSClient, moto_sqs_client: SQSClient) -> None:
    await snssqs_client.subscribe_to(moto_sns_client, moto_sqs_client, topic="test-topic", queue="test-queue")
    await snssqs_client.publish(moto_sns_client, "test-topic", {"message": "1"}, JsonBase)
    await snssqs_client.publish(moto_sns_client, "test-topic", {"message": "2"}, JsonBase)

    messages = await snssqs_client.receive(moto_sqs_client, "test-queue", JsonBase, Dict[str, str])

    assert messages == [{"message": "1"}, {"message": "2"}]


@pytest.mark.asyncio()
async def test_received_messages_are_deleted_from_queue(moto_sns_client: SNSClient, moto_sqs_client: SQSClient) -> None:
    await snssqs_client.subscribe_to(moto_sns_client, moto_sqs_client, topic="test-topic", queue="test-queue")
    await snssqs_client.publish(moto_sns_client, "test-topic", {"message": "1"}, JsonBase)

    await snssqs_client.receive(moto_sqs_client, "test-queue", JsonBase, Dict[str, str])

    queue_attributes = await snssqs_client.get_queue_attributes(
        moto_sqs_client, queue="test-queue", attributes=["ApproximateNumberOfMessagesNotVisible"]
    )
    assert queue_attributes["ApproximateNumberOfMessagesNotVisible"] == "0"


@pytest.mark.asyncio()
async def test_receive_max_receive_messages(moto_sns_client: SNSClient, moto_sqs_client: SQSClient) -> None:
    await snssqs_client.subscribe_to(moto_sns_client, moto_sqs_client, topic="test-topic", queue="test-queue")
    await snssqs_client.publish(moto_sns_client, "test-topic", {"message": "1"}, JsonBase)
    await snssqs_client.publish(moto_sns_client, "test-topic", {"message": "2"}, JsonBase)

    messages = await snssqs_client.receive(moto_sqs_client, "test-queue", JsonBase, Dict[str, str], max_messages=1)
    assert messages == [{"message": "1"}]

    messages = await snssqs_client.receive(moto_sqs_client, "test-queue", JsonBase, Dict[str, str], max_messages=1)
    assert messages == [{"message": "2"}]


@pytest.mark.asyncio()
async def test_publish_and_receive_protobuf_message(moto_sns_client: SNSClient, moto_sqs_client: SQSClient) -> None:
    await snssqs_client.subscribe_to(moto_sns_client, moto_sqs_client, topic="test-topic", queue="test-queue")
    await snssqs_client.publish(moto_sns_client, "test-topic", Person(id="123456", name="John Doe"), ProtobufBase)

    messages = await snssqs_client.receive(moto_sqs_client, "test-queue", ProtobufBase, Person)

    assert messages == [Person(id="123456", name="John Doe")]
