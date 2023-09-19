import logging
from socket import socket
from typing import TypedDict


class AWSClientConfig(TypedDict):
    region_name: str
    aws_access_key_id: str
    aws_secret_access_key: str
    endpoint_url: str


def get_available_port() -> int:
    with socket() as sock:
        sock.bind(("", 0))
        return int(sock.getsockname()[1])


def setup_logger(name: str) -> logging.Logger:
    """Outputs logs to stderr for better visibility in pytest output.

    Inspired by testcontainers.core.utils.setup_logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter(fmt="%(name)s: %(message)s"))
    logger.addHandler(handler)
    return logger
