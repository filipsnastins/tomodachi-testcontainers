import json
from typing import Any, Dict, List, Protocol, Type, TypeVar, Union

from types_aiobotocore_sns import SNSClient
from types_aiobotocore_sqs import SQSClient
from types_aiobotocore_sqs.literals import QueueAttributeFilterType, QueueAttributeNameType

MessageType = TypeVar("MessageType")


class TomodachiSNSSQSEnvelopeStatic(Protocol):
    @classmethod
    async def build_message(
        cls: "TomodachiSNSSQSEnvelopeStatic", service: Any, topic: str, data: Any, **kwargs: Any
    ) -> str:
        ...

    @classmethod
    async def parse_message(cls: "TomodachiSNSSQSEnvelopeStatic", payload: str, **kwargs: Any) -> Union[dict, tuple]:
        ...


class TomodachiSNSSQSEnvelopeInstance(Protocol):
    async def build_message(
        self: "TomodachiSNSSQSEnvelopeInstance", service: Any, topic: str, data: Any, **kwargs: Any
    ) -> str:
        ...

    async def parse_message(self: "TomodachiSNSSQSEnvelopeInstance", payload: str, **kwargs: Any) -> Union[dict, tuple]:
        ...


TomodachiSNSSQSEnvelope = Union[TomodachiSNSSQSEnvelopeStatic, TomodachiSNSSQSEnvelopeInstance]


async def subscribe_to(sns_client: SNSClient, sqs_client: SQSClient, topic: str, queue: str) -> None:
    """Subscribe a SQS queue to a SNS topic; create the topic and queue if they don't exist."""
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
    queue: str,
    envelope: TomodachiSNSSQSEnvelope,
    message_type: Type[MessageType],
    max_messages: int = 10,
) -> List[MessageType]:
    """Receive messages from a SQS queue."""
    get_queue_url_response = await sqs_client.get_queue_url(QueueName=queue)
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
        await sqs_client.delete_message(QueueUrl=queue_url, ReceiptHandle=received_message["ReceiptHandle"])
    return parsed_messages


async def publish(sns_client: SNSClient, topic: str, data: Any, envelope: TomodachiSNSSQSEnvelopeStatic) -> None:
    """Publish a message to a SNS topic."""
    message = await envelope.build_message(service={}, topic=topic, data=data)

    list_topics_response = await sns_client.list_topics()
    topic_arn = next((v["TopicArn"] for v in list_topics_response["Topics"] if v["TopicArn"].endswith(topic)), None)
    if not topic_arn:
        raise ValueError(f"Topic does not exist: {topic}")

    await sns_client.publish(TopicArn=topic_arn, Message=message)


async def get_queue_attributes(
    sqs_client: SQSClient, queue: str, attributes: List[QueueAttributeFilterType]
) -> Dict[QueueAttributeNameType, str]:
    """Get attributes for a SQS queue."""
    get_queue_response = await sqs_client.get_queue_url(QueueName=queue)
    queue_url = get_queue_response["QueueUrl"]
    get_queue_attributes_response = await sqs_client.get_queue_attributes(QueueUrl=queue_url, AttributeNames=attributes)
    return get_queue_attributes_response["Attributes"]
