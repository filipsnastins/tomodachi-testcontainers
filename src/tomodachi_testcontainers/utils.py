import io
import logging
import os
import tarfile
from pathlib import Path
from socket import socket
from typing import Dict, Optional, TypedDict, cast

import requests
from docker.errors import ImageNotFound
from docker.models.containers import Container
from docker.models.images import Image as DockerImage
from tenacity import Retrying
from tenacity.stop import stop_after_delay
from tenacity.wait import wait_fixed
from testcontainers.core.docker_client import DockerClient


class AWSClientConfig(TypedDict):
    region_name: str
    aws_access_key_id: str
    aws_secret_access_key: str
    endpoint_url: str


def get_docker_image(image_id: str, docker_client_kw: Optional[Dict] = None) -> DockerImage:
    """Returns a Docker image, pulling it if not exists on host."""
    client = DockerClient(**(docker_client_kw or {}))
    try:
        return cast(DockerImage, client.client.images.get(image_id))
    except ImageNotFound:
        return cast(DockerImage, client.client.images.pull(image_id))


def copy_folder_to_container(container: Container, host_path: Path, container_path: Path) -> None:
    """Copies a folder from the host to the container."""
    tar_stream = io.BytesIO()
    with tarfile.open(fileobj=tar_stream, mode="w") as tar:
        for root, _, files in os.walk(host_path):
            for file in files:
                file_path = Path(root) / file
                arcname = os.path.relpath(file_path, host_path)
                tar.add(file_path, arcname=arcname)
    tar_stream.seek(0)
    container.put_archive(path=container_path, data=tar_stream)


def wait_for_http_healthcheck(url: str, timeout: float = 10.0, interval: float = 0.5, status_code: int = 200) -> None:
    """Waits until the HTTP URL returns the expected status code."""
    for attempt in Retrying(stop=stop_after_delay(timeout), wait=wait_fixed(interval), reraise=True):
        with attempt:
            response = requests.get(url, timeout=timeout)
            if response.status_code != status_code:
                raise RuntimeError(f"Healthcheck failed with HTTP status code: {response.status_code}")


def get_available_port() -> int:
    """Returns a random available port on the host."""
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
