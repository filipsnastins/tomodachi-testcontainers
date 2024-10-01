import json
import re
from typing import Dict

import pytest
from tomodachi.envelope.json_base import JsonBase
from tomodachi.envelope.protobuf_base import ProtobufBase
from types_aiobotocore_sns import SNSClient
from types_aiobotocore_sqs import SQSClient

from tomodachi_testcontainers.clients import SNSSQSTestClient
from tomodachi_testcontainers.clients.snssqs import QueueDoesNotExistError, SQSMessage, TopicDoesNotExistError

from .proto.person_pb2 import Person

pytestmark = pytest.mark.usefixtures("reset_moto_container_on_teardown")


@pytest.fixture
def snssqs_test_client(moto_sns_client: SNSClient, moto_sqs_client: SQSClient) -> SNSSQSTestClient:
    return SNSSQSTestClient(moto_sns_client, moto_sqs_client)


@pytest.mark.asyncio(loop_scope="session")
async def test_no_messages_received(snssqs_test_client: SNSSQSTestClient) -> None:
    await snssqs_test_client.subscribe_to(topic="topic", queue="queue")

    messages = await snssqs_test_client.receive("queue", JsonBase, Dict[str, str])

    assert messages == []


@pytest.mark.asyncio(loop_scope="session")
async def test_publish_fails_if_topic_does_not_exist(snssqs_test_client: SNSSQSTestClient) -> None:
    with pytest.raises(TopicDoesNotExistError, match="topic"):
        await snssqs_test_client.publish("topic", {"message": "1"}, JsonBase)


@pytest.mark.asyncio(loop_scope="session")
async def test_publish_and_receive_messages(snssqs_test_client: SNSSQSTestClient) -> None:
    await snssqs_test_client.subscribe_to(topic="topic", queue="queue")

    await snssqs_test_client.publish("topic", {"message": "1"}, JsonBase)
    await snssqs_test_client.publish("topic", {"message": "2"}, JsonBase)

    messages = await snssqs_test_client.receive("queue", JsonBase, Dict[str, str])
    assert messages == [
        SQSMessage({"message": "1"}),
        SQSMessage({"message": "2"}),
    ]


@pytest.mark.asyncio(loop_scope="session")
async def test_publish_and_receive_with_message_attributes(snssqs_test_client: SNSSQSTestClient) -> None:
    await snssqs_test_client.subscribe_to(
        topic="topic",
        queue="queue",
        subscribe_attributes={"FilterPolicy": json.dumps({"MyMessageAttribute": ["will-be-included"]})},
    )

    await snssqs_test_client.publish(
        "topic",
        {"message": "1"},
        JsonBase,
        message_attributes={"MyMessageAttribute": {"DataType": "String", "StringValue": "will-be-included"}},
    )
    await snssqs_test_client.publish(
        "topic",
        {"message": "2"},
        JsonBase,
        message_attributes={"MyMessageAttribute": {"DataType": "String", "StringValue": "not-included"}},
    )

    messages = await snssqs_test_client.receive("queue", JsonBase, Dict[str, str])
    assert messages == [
        SQSMessage(
            payload={"message": "1"},
            message_attributes={"MyMessageAttribute": {"Type": "String", "Value": "will-be-included"}},
        )
    ]


@pytest.mark.asyncio(loop_scope="session")
async def test_publish_and_receive_with_fifo(snssqs_test_client: SNSSQSTestClient) -> None:
    await snssqs_test_client.subscribe_to(topic="topic.fifo", queue="queue.fifo")

    await snssqs_test_client.publish(
        "topic.fifo", {"message": "1"}, JsonBase, message_deduplication_id="123456", message_group_id="123456"
    )
    await snssqs_test_client.publish(
        "topic.fifo", {"message": "1"}, JsonBase, message_deduplication_id="123456", message_group_id="123456"
    )

    messages = await snssqs_test_client.receive("queue.fifo", JsonBase, Dict[str, str])
    assert messages == [SQSMessage({"message": "1"})]


@pytest.mark.asyncio(loop_scope="session")
async def test_send_fails_if_queue_does_not_exist(snssqs_test_client: SNSSQSTestClient) -> None:
    with pytest.raises(QueueDoesNotExistError, match="queue"):
        await snssqs_test_client.send("queue", {"message": "1"}, JsonBase)


@pytest.mark.asyncio(loop_scope="session")
async def test_send_and_receive_message(snssqs_test_client: SNSSQSTestClient) -> None:
    await snssqs_test_client.create_queue("queue")

    await snssqs_test_client.send("queue", {"message": "1"}, JsonBase)
    await snssqs_test_client.send("queue", {"message": "2"}, JsonBase)

    messages = await snssqs_test_client.receive("queue", JsonBase, Dict[str, str])
    assert messages == [SQSMessage({"message": "1"}), SQSMessage({"message": "2"})]


@pytest.mark.asyncio(loop_scope="session")
async def test_send_and_receive_message_with_fifo(snssqs_test_client: SNSSQSTestClient) -> None:
    await snssqs_test_client.create_queue("queue.fifo")

    await snssqs_test_client.send(
        "queue.fifo", {"message": "1"}, JsonBase, message_deduplication_id="123456", message_group_id="123456"
    )
    await snssqs_test_client.send(
        "queue.fifo", {"message": "2"}, JsonBase, message_deduplication_id="123456", message_group_id="123456"
    )

    messages = await snssqs_test_client.receive("queue.fifo", JsonBase, Dict[str, str])
    assert messages == [SQSMessage({"message": "1"})]


@pytest.mark.asyncio(loop_scope="session")
async def test_send_and_receive_messages_with_attributes(snssqs_test_client: SNSSQSTestClient) -> None:
    await snssqs_test_client.create_queue("queue")

    await snssqs_test_client.send(
        "queue",
        {"message": "1"},
        JsonBase,
        message_attributes={"MyMessageAttribute": {"DataType": "String", "StringValue": "test-value"}},
    )

    messages = await snssqs_test_client.receive("queue", JsonBase, Dict[str, str])
    assert messages == [
        SQSMessage(
            payload={"message": "1"},
            message_attributes={"MyMessageAttribute": {"DataType": "String", "StringValue": "test-value"}},
        )
    ]


@pytest.mark.asyncio(loop_scope="session")
async def test_received_messages_are_deleted_from_queue(snssqs_test_client: SNSSQSTestClient) -> None:
    await snssqs_test_client.subscribe_to(topic="topic", queue="queue")
    await snssqs_test_client.publish("topic", {"message": "1"}, JsonBase)

    await snssqs_test_client.receive("queue", JsonBase, Dict[str, str])

    queue_attributes = await snssqs_test_client.get_queue_attributes(
        "queue", attributes=["ApproximateNumberOfMessagesNotVisible"]
    )
    assert queue_attributes["ApproximateNumberOfMessagesNotVisible"] == "0"


@pytest.mark.asyncio(loop_scope="session")
async def test_receive_max_receive_messages(snssqs_test_client: SNSSQSTestClient) -> None:
    await snssqs_test_client.subscribe_to(topic="topic", queue="queue")
    await snssqs_test_client.publish("topic", {"message": "1"}, JsonBase)
    await snssqs_test_client.publish("topic", {"message": "2"}, JsonBase)

    messages = await snssqs_test_client.receive("queue", JsonBase, Dict[str, str], max_messages=1)
    assert messages == [SQSMessage({"message": "1"})]

    messages = await snssqs_test_client.receive("queue", JsonBase, Dict[str, str], max_messages=1)
    assert messages == [SQSMessage({"message": "2"})]


@pytest.mark.asyncio(loop_scope="session")
async def test_publish_and_receive_protobuf_message(snssqs_test_client: SNSSQSTestClient) -> None:
    await snssqs_test_client.subscribe_to(topic="topic", queue="queue")
    await snssqs_test_client.publish("topic", Person(id="123456", name="John Doe"), ProtobufBase)

    messages = await snssqs_test_client.receive("queue", ProtobufBase, Person)

    assert messages == [SQSMessage(Person(id="123456", name="John Doe"))]


@pytest.mark.asyncio(loop_scope="session")
async def test_purge_queue(snssqs_test_client: SNSSQSTestClient) -> None:
    await snssqs_test_client.subscribe_to(topic="topic", queue="queue")
    await snssqs_test_client.publish("topic", {"message": "1"}, JsonBase)

    await snssqs_test_client.purge_queue("queue")

    messages = await snssqs_test_client.receive("queue", JsonBase, Dict[str, str])
    assert messages == []


@pytest.mark.asyncio(loop_scope="session")
async def test_subscribe_to_creates_fifo_queue_and_topic(snssqs_test_client: SNSSQSTestClient) -> None:
    await snssqs_test_client.subscribe_to(topic="topic.fifo", queue="queue.fifo")

    queue_attributes = await snssqs_test_client.get_queue_attributes("queue.fifo", attributes=["FifoQueue"])
    assert queue_attributes["FifoQueue"] == "true"

    topic_attributes = await snssqs_test_client.get_topic_attributes("topic.fifo")
    assert topic_attributes["FifoTopic"] == "true"


@pytest.mark.asyncio(loop_scope="session")
async def test_queue_attribute_getters(snssqs_test_client: SNSSQSTestClient) -> None:
    await snssqs_test_client.subscribe_to(topic="topic", queue="queue")

    queue_arn = await snssqs_test_client.get_queue_arn("queue")
    queue_url = await snssqs_test_client.get_queue_url("queue")
    queue_attributes = await snssqs_test_client.get_queue_attributes("queue", attributes=["QueueArn"])

    assert queue_arn == "arn:aws:sqs:us-east-1:123456789012:queue"
    assert re.match(r"^http://localhost:\d+/123456789012/queue", queue_url)
    assert queue_attributes["QueueArn"] == queue_arn


@pytest.mark.asyncio(loop_scope="session")
async def test_queue_attribute_getters__raise_when_queue_does_not_exist(snssqs_test_client: SNSSQSTestClient) -> None:
    with pytest.raises(QueueDoesNotExistError, match="queue"):
        await snssqs_test_client.get_queue_arn("queue")

    with pytest.raises(QueueDoesNotExistError, match="queue"):
        await snssqs_test_client.get_queue_url("queue")

    with pytest.raises(QueueDoesNotExistError, match="queue"):
        await snssqs_test_client.get_queue_attributes("queue", attributes=[])


@pytest.mark.asyncio(loop_scope="session")
async def test_topic_attribute_getters(snssqs_test_client: SNSSQSTestClient) -> None:
    await snssqs_test_client.subscribe_to(topic="topic", queue="queue")

    topic_arn = await snssqs_test_client.get_topic_arn("topic")
    topic_attributes = await snssqs_test_client.get_topic_attributes("topic")

    assert topic_arn == "arn:aws:sns:us-east-1:123456789012:topic"
    assert topic_attributes["TopicArn"] == topic_arn


@pytest.mark.asyncio(loop_scope="session")
async def test_topic_attribute_getters__raise_when_topic_does_not_exist(snssqs_test_client: SNSSQSTestClient) -> None:
    with pytest.raises(TopicDoesNotExistError, match="topic"):
        await snssqs_test_client.get_topic_arn("topic")

    with pytest.raises(TopicDoesNotExistError, match="topic"):
        await snssqs_test_client.get_topic_attributes("topic")
