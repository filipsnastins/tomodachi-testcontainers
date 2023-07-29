import json
from typing import Any, List, Protocol, Type, TypeVar, Union

from types_aiobotocore_sns import SNSClient
from types_aiobotocore_sqs import SQSClient

MessageType = TypeVar("MessageType")


class TomodachiSNSSQSEnvelope(Protocol):
    @classmethod
    async def build_message(cls: "TomodachiSNSSQSEnvelope", service: Any, topic: str, data: Any, **kwargs: Any) -> str:
        ...

    @classmethod
    async def parse_message(cls: "TomodachiSNSSQSEnvelope", payload: str, **kwargs: Any) -> Union[dict, tuple]:
        ...


async def subscribe_to(sns_client: SNSClient, sqs_client: SQSClient, topic: str, queue: str) -> None:
    create_topic_response = await sns_client.create_topic(Name=topic)
    topic_arn = create_topic_response["TopicArn"]

    create_queue_response = await sqs_client.create_queue(QueueName=queue)
    queue_url = create_queue_response["QueueUrl"]

    get_queue_attributes_response = await sqs_client.get_queue_attributes(
        QueueUrl=queue_url, AttributeNames=["QueueArn"]
    )
    queue_arn = get_queue_attributes_response["Attributes"]["QueueArn"]

    await sns_client.subscribe(TopicArn=topic_arn, Protocol="sqs", Endpoint=queue_arn)


async def receive(
    sqs_client: SQSClient,
    queue_name: str,
    envelope: TomodachiSNSSQSEnvelope,
    message_type: Type[MessageType],
    max_messages: int = 10,
) -> List[MessageType]:
    get_queue_url_response = await sqs_client.get_queue_url(QueueName=queue_name)
    queue_url = get_queue_url_response["QueueUrl"]

    received_messages_response = await sqs_client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=max_messages)
    received_messages = received_messages_response.get("Messages")
    if not received_messages:
        return []

    parsed_messages: List[MessageType] = []
    for received_message in received_messages:
        payload = json.loads(received_message["Body"])["Message"]
        parsed_message = await envelope.parse_message(payload=payload, proto_class=message_type)
        parsed_messages.append(parsed_message[0]["data"])
    return parsed_messages


async def publish(sns_client: SNSClient, topic: str, data: Any, envelope: TomodachiSNSSQSEnvelope) -> None:
    message = await envelope.build_message(service={}, topic=topic, data=data)

    create_topic_response = await sns_client.create_topic(Name=topic)
    topic_arn = create_topic_response["TopicArn"]

    await sns_client.publish(TopicArn=topic_arn, Message=message)
