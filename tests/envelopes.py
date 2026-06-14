"""Tomodachi SNS/SQS message envelopes used by the test suite.

These classes are copied verbatim (behaviour-wise) from the ``tomodachi`` package
(``tomodachi.envelope.json_base`` and ``tomodachi.envelope.protobuf_base``) so the
test suite does not depend on ``tomodachi`` as a direct dependency.
"""

import base64
import json
import logging
import time
import uuid
import zlib
from typing import Any, Union

from .clients.proto.sns_sqs_message_pb2 import SNSSQSMessage

JSON_PROTOCOL_VERSION = "tomodachi-json-base--1.0.0"
PROTOBUF_PROTOCOL_VERSION = "tomodachi-protobuf-base--1.0.0"

__all__ = [
    "JsonBase",
    "ProtobufBase",
    "SNSSQSMessage",
]


class JsonBase:
    @classmethod
    async def build_message(cls, service: Any, topic: str, data: Any, **kwargs: Any) -> str:
        data_encoding = "raw"
        if len(json.dumps(data)) >= 60000:
            data = base64.b64encode(zlib.compress(json.dumps(data).encode("utf-8"))).decode("utf-8")
            data_encoding = "base64_gzip_json"

        message = {
            "service": {"name": getattr(service, "name", None), "uuid": getattr(service, "uuid", None)},
            "metadata": {
                "message_uuid": f"{getattr(service, 'uuid', '')}.{uuid.uuid4()}",
                "protocol_version": JSON_PROTOCOL_VERSION,
                "compatible_protocol_versions": ["json_base-wip"],  # deprecated
                "timestamp": time.time(),
                "topic": topic,
                "data_encoding": data_encoding,
            },
            "data": data,
        }
        return json.dumps(message)

    @classmethod
    async def parse_message(cls, payload: str, **kwargs: Any) -> Union[dict, tuple]:
        message = json.loads(payload)

        message_uuid = message.get("metadata", {}).get("message_uuid")
        timestamp = message.get("metadata", {}).get("timestamp")

        data = None
        if message.get("metadata", {}).get("data_encoding") == "raw":
            data = message.get("data")
        elif message.get("metadata", {}).get("data_encoding") == "base64_gzip_json":
            data = json.loads(zlib.decompress(base64.b64decode(message.get("data").encode("utf-8"))).decode("utf-8"))

        return (
            {
                "service": {
                    "name": message.get("service", {}).get("name"),
                    "uuid": message.get("service", {}).get("uuid"),
                },
                "metadata": {
                    "message_uuid": message.get("metadata", {}).get("message_uuid"),
                    "protocol_version": message.get("metadata", {}).get("protocol_version"),
                    "timestamp": message.get("metadata", {}).get("timestamp"),
                    "topic": message.get("metadata", {}).get("topic"),
                    "data_encoding": message.get("metadata", {}).get("data_encoding"),
                },
                "data": data,
            },
            message_uuid,
            timestamp,
        )


class ProtobufBase:
    @classmethod
    async def build_message(cls, service: Any, topic: str, data: Any, **kwargs: Any) -> str:
        message_data = data.SerializeToString()

        data_encoding = "proto"
        if len(message_data) > 60000:
            message_data = zlib.compress(data.SerializeToString())
            data_encoding = "gzip_proto"

        message = SNSSQSMessage()
        message.service.name = str(getattr(service, "name", None) or "")
        message.service.uuid = str(getattr(service, "uuid", None) or "")
        message.metadata.message_uuid = f"{getattr(service, 'uuid', '')}.{uuid.uuid4()}"
        message.metadata.protocol_version = PROTOBUF_PROTOCOL_VERSION
        message.metadata.timestamp = time.time()
        message.metadata.topic = topic
        message.metadata.data_encoding = data_encoding
        message.data = message_data

        return base64.b64encode(message.SerializeToString()).decode("ascii")

    @classmethod
    async def parse_message(
        cls, payload: str, proto_class: Any = None, validator: Any = None, **kwargs: Any
    ) -> Union[dict, tuple]:
        message = SNSSQSMessage()
        message.ParseFromString(base64.b64decode(payload))

        message_uuid = message.metadata.message_uuid
        timestamp = message.metadata.timestamp

        raw_data = None
        obj = None

        if not proto_class:
            raw_data = message.data
        else:
            obj = proto_class()
            if message.metadata.data_encoding == "proto":
                obj.ParseFromString(message.data)
            elif message.metadata.data_encoding == "base64":  # deprecated
                obj.ParseFromString(base64.b64decode(message.data))
            elif message.metadata.data_encoding == "gzip_proto":
                obj.ParseFromString(zlib.decompress(message.data))
            elif message.metadata.data_encoding == "base64_gzip_proto":  # deprecated
                obj.ParseFromString(zlib.decompress(base64.b64decode(message.data)))
            elif message.metadata.data_encoding == "raw":
                raw_data = message.data

        if validator is not None:
            try:
                if hasattr(validator, "__func__"):
                    # for static functions
                    validator.__func__(obj)
                else:
                    # for non-static functions
                    validator(obj)
            except Exception as e:
                logging.getLogger("tomodachi.envelope").warning(str(e))
                raise

        return (
            {
                "service": {"name": message.service.name, "uuid": message.service.uuid},
                "metadata": {
                    "message_uuid": message.metadata.message_uuid,
                    "protocol_version": message.metadata.protocol_version,
                    "timestamp": message.metadata.timestamp,
                    "topic": message.metadata.topic,
                    "data_encoding": message.metadata.data_encoding,
                },
                "data": raw_data if raw_data is not None else obj,
            },
            message_uuid,
            timestamp,
        )
