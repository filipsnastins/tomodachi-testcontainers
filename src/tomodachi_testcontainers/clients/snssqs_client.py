import json
from typing import Any, Dict, List, Mapping, Optional, Protocol, Type, TypeVar, Union

from types_aiobotocore_sns import SNSClient
from types_aiobotocore_sns.type_defs import MessageAttributeValueTypeDef
from types_aiobotocore_sqs import SQSClient
from types_aiobotocore_sqs.literals import QueueAttributeFilterType, QueueAttributeNameType

__all__ = [
    "SNSSQSTestClient",
]

MessageType = TypeVar("MessageType")


class _TomodachiSNSSQSEnvelopeStatic(Protocol):
    @classmethod
    async def build_message(
        cls: "_TomodachiSNSSQSEnvelopeStatic", service: Any, topic: str, data: Any, **kwargs: Any
    ) -> str:
        ...

    @classmethod
    async def parse_message(cls: "_TomodachiSNSSQSEnvelopeStatic", payload: str, **kwargs: Any) -> Union[dict, tuple]:
        ...


class _TomodachiSNSSQSEnvelopeInstance(Protocol):
    async def build_message(
        self: "_TomodachiSNSSQSEnvelopeInstance", service: Any, topic: str, data: Any, **kwargs: Any
    ) -> str:
        ...

    async def parse_message(
        self: "_TomodachiSNSSQSEnvelopeInstance", payload: str, **kwargs: Any
    ) -> Union[dict, tuple]:
        ...


TomodachiSNSSQSEnvelope = Union[_TomodachiSNSSQSEnvelopeStatic, _TomodachiSNSSQSEnvelopeInstance]


class SNSSQSTestClient:
    """Wraps aiobotocore SNS and SQS clients and provides common methods for testing SNS SQS integrations."""

    def __init__(self, sns_client: SNSClient, sqs_client: SQSClient) -> None:
        self.sns_client = sns_client
        self.sqs_client = sqs_client

    async def subscribe_to(
        self, topic: str, queue: str, fifo: bool = False, subscribe_attributes: Optional[Mapping[str, str]] = None
    ) -> None:
        """Subscribe a SQS queue to a SNS topic; create the topic and queue if they don't exist."""
        list_topics_response = await self.sns_client.list_topics()
        topic_arn = next((v["TopicArn"] for v in list_topics_response["Topics"] if v["TopicArn"].endswith(topic)), None)

        topic_attributes: Mapping[str, str] = {}
        queue_attributes: Mapping[QueueAttributeNameType, str] = {}
        if fifo:
            topic_attributes = {
                "FifoTopic": "true",
                "ContentBasedDeduplication": "false",
            }
            queue_attributes = {
                "FifoQueue": "true",
                "ContentBasedDeduplication": "false",
            }

        if not topic_arn:
            create_topic_response = await self.sns_client.create_topic(Name=topic, Attributes=topic_attributes)
            topic_arn = create_topic_response["TopicArn"]

        create_queue_response = await self.sqs_client.create_queue(QueueName=queue, Attributes=queue_attributes)
        queue_url = create_queue_response["QueueUrl"]

        get_queue_attributes_response = await self.sqs_client.get_queue_attributes(
            QueueUrl=queue_url, AttributeNames=["QueueArn"]
        )
        queue_arn = get_queue_attributes_response["Attributes"]["QueueArn"]

        await self.sns_client.subscribe(
            TopicArn=topic_arn,
            Protocol="sqs",
            Endpoint=queue_arn,
            Attributes=subscribe_attributes or {},
        )

    async def receive(
        self, queue: str, envelope: TomodachiSNSSQSEnvelope, message_type: Type[MessageType], max_messages: int = 10
    ) -> List[MessageType]:
        """Receive messages from a SQS queue."""
        get_queue_url_response = await self.sqs_client.get_queue_url(QueueName=queue)
        queue_url = get_queue_url_response["QueueUrl"]

        received_messages_response = await self.sqs_client.receive_message(
            QueueUrl=queue_url, MaxNumberOfMessages=max_messages
        )
        received_messages = received_messages_response.get("Messages")
        if not received_messages:
            return []

        parsed_messages: List[MessageType] = []
        for received_message in received_messages:
            payload = json.loads(received_message["Body"])["Message"]
            parsed_message = await envelope.parse_message(payload=payload, proto_class=message_type)
            parsed_messages.append(parsed_message[0]["data"])
            await self.sqs_client.delete_message(QueueUrl=queue_url, ReceiptHandle=received_message["ReceiptHandle"])
        return parsed_messages

    async def publish(
        self,
        topic: str,
        data: Any,
        envelope: TomodachiSNSSQSEnvelope,
        message_attributes: Optional[Mapping[str, MessageAttributeValueTypeDef]] = None,
        message_deduplication_id: Optional[str] = None,
        message_group_id: Optional[str] = None,
    ) -> None:
        """Publish a message to a SNS topic."""
        message = await envelope.build_message(service={}, topic=topic, data=data)

        list_topics_response = await self.sns_client.list_topics()
        topic_arn = next((v["TopicArn"] for v in list_topics_response["Topics"] if v["TopicArn"].endswith(topic)), None)
        if not topic_arn:
            raise ValueError(f"Topic does not exist: {topic}")

        kwargs: Dict[str, Any] = {}
        if message_attributes:
            kwargs["MessageAttributes"] = message_attributes
        if message_deduplication_id:
            kwargs["MessageDeduplicationId"] = message_deduplication_id
        if message_group_id:
            kwargs["MessageGroupId"] = message_group_id

        await self.sns_client.publish(TopicArn=topic_arn, Message=message, **kwargs)

    async def get_queue_attributes(
        self, queue: str, attributes: List[QueueAttributeFilterType]
    ) -> Dict[QueueAttributeNameType, str]:
        """Get attributes for a SQS queue."""
        get_queue_response = await self.sqs_client.get_queue_url(QueueName=queue)
        queue_url = get_queue_response["QueueUrl"]
        get_queue_attributes_response = await self.sqs_client.get_queue_attributes(
            QueueUrl=queue_url, AttributeNames=attributes
        )
        return get_queue_attributes_response["Attributes"]
