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
