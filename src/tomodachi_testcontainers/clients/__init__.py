"""Test clients for testing interactions with external systems, like AWS SNS/SQS."""

from .snssqs import SNSSQSTestClient

__all__ = [
    "SNSSQSTestClient",
]
