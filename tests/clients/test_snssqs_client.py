import json
from typing import Dict

import pytest
from tomodachi.envelope.json_base import JsonBase
from tomodachi.envelope.protobuf_base import ProtobufBase
from types_aiobotocore_sns import SNSClient
from types_aiobotocore_sqs import SQSClient

from tests.clients.proto_build.message_pb2 import Person
from tomodachi_testcontainers.clients import SNSSQSTestClient

pytestmark = pytest.mark.usefixtures("_reset_moto_container_on_teardown")


@pytest.fixture()
def snssqs_test_client(moto_sns_client: SNSClient, moto_sqs_client: SQSClient) -> SNSSQSTestClient:
    return SNSSQSTestClient(moto_sns_client, moto_sqs_client)


@pytest.mark.asyncio()
async def test_no_messages_received(snssqs_test_client: SNSSQSTestClient) -> None:
    await snssqs_test_client.subscribe_to(topic="test-topic", queue="test-queue")

    messages = await snssqs_test_client.receive("test-queue", JsonBase, Dict[str, str])

    assert messages == []


@pytest.mark.asyncio()
async def test_publish_fails_if_topic_does_not_exist(snssqs_test_client: SNSSQSTestClient) -> None:
    with pytest.raises(ValueError, match="Topic does not exist: test-topic"):
        await snssqs_test_client.publish("test-topic", {"message": "1"}, JsonBase)


@pytest.mark.asyncio()
async def test_publish_and_receive_messages(snssqs_test_client: SNSSQSTestClient) -> None:
    await snssqs_test_client.subscribe_to(topic="test-topic", queue="test-queue")
    await snssqs_test_client.publish("test-topic", {"message": "1"}, JsonBase)
    await snssqs_test_client.publish("test-topic", {"message": "2"}, JsonBase)

    messages = await snssqs_test_client.receive("test-queue", JsonBase, Dict[str, str])

    assert messages == [{"message": "1"}, {"message": "2"}]


@pytest.mark.asyncio()
async def test_publish_and_receive_with_message_attributes(snssqs_test_client: SNSSQSTestClient) -> None:
    await snssqs_test_client.subscribe_to(
        topic="test-topic",
        queue="test-queue",
        attributes={"FilterPolicy": json.dumps({"MyMessageAttribute": ["will-be-included"]})},
    )

    await snssqs_test_client.publish(
        "test-topic",
        {"message": "1"},
        JsonBase,
        message_attributes={"MyMessageAttribute": {"DataType": "String", "StringValue": "will-be-included"}},
    )
    await snssqs_test_client.publish(
        "test-topic",
        {"message": "2"},
        JsonBase,
        message_attributes={"MyMessageAttribute": {"DataType": "String", "StringValue": "not-included"}},
    )

    messages = await snssqs_test_client.receive("test-queue", JsonBase, Dict[str, str])
    assert messages == [{"message": "1"}]


@pytest.mark.asyncio()
async def test_publish_and_receive_with_fifo(snssqs_test_client: SNSSQSTestClient) -> None:
    await snssqs_test_client.sns_client.create_topic(
        Name="test-topic.fifo", Attributes={"FifoTopic": "true", "ContentBasedDeduplication": "false"}
    )
    await snssqs_test_client.sqs_client.create_queue(
        QueueName="test-queue.fifo", Attributes={"FifoQueue": "true", "ContentBasedDeduplication": "false"}
    )
    await snssqs_test_client.subscribe_to(topic="test-topic.fifo", queue="test-queue.fifo")

    await snssqs_test_client.publish(
        "test-topic.fifo", {"message": "1"}, JsonBase, message_deduplication_id="123456", message_group_id="123456"
    )
    await snssqs_test_client.publish(
        "test-topic.fifo", {"message": "1"}, JsonBase, message_deduplication_id="123456", message_group_id="123456"
    )

    messages = await snssqs_test_client.receive("test-queue.fifo", JsonBase, Dict[str, str])
    assert messages == [{"message": "1"}]


@pytest.mark.asyncio()
async def test_received_messages_are_deleted_from_queue(snssqs_test_client: SNSSQSTestClient) -> None:
    await snssqs_test_client.subscribe_to(topic="test-topic", queue="test-queue")
    await snssqs_test_client.publish("test-topic", {"message": "1"}, JsonBase)

    await snssqs_test_client.receive("test-queue", JsonBase, Dict[str, str])

    queue_attributes = await snssqs_test_client.get_queue_attributes(
        queue="test-queue", attributes=["ApproximateNumberOfMessagesNotVisible"]
    )
    assert queue_attributes["ApproximateNumberOfMessagesNotVisible"] == "0"


@pytest.mark.asyncio()
async def test_receive_max_receive_messages(snssqs_test_client: SNSSQSTestClient) -> None:
    await snssqs_test_client.subscribe_to(topic="test-topic", queue="test-queue")
    await snssqs_test_client.publish("test-topic", {"message": "1"}, JsonBase)
    await snssqs_test_client.publish("test-topic", {"message": "2"}, JsonBase)

    messages = await snssqs_test_client.receive("test-queue", JsonBase, Dict[str, str], max_messages=1)
    assert messages == [{"message": "1"}]

    messages = await snssqs_test_client.receive("test-queue", JsonBase, Dict[str, str], max_messages=1)
    assert messages == [{"message": "2"}]


@pytest.mark.asyncio()
async def test_publish_and_receive_protobuf_message(snssqs_test_client: SNSSQSTestClient) -> None:
    await snssqs_test_client.subscribe_to(topic="test-topic", queue="test-queue")
    await snssqs_test_client.publish("test-topic", Person(id="123456", name="John Doe"), ProtobufBase)

    messages = await snssqs_test_client.receive("test-queue", ProtobufBase, Person)

    assert messages == [Person(id="123456", name="John Doe")]
