import io
import logging
import os
import socket
import tarfile
from pathlib import Path
from typing import Dict, Optional, TypedDict, cast

from docker.errors import ImageNotFound
from docker.models.containers import Container
from docker.models.images import Image
from testcontainers.core.docker_client import DockerClient


class AWSClientConfig(TypedDict):
    region_name: str
    aws_access_key_id: str
    aws_secret_access_key: str
    endpoint_url: str


def get_docker_image(image_id: str, docker_client_kwargs: Optional[Dict] = None) -> Image:
    """Returns a Docker image, pulling it if not exists on host."""
    client = DockerClient(**(docker_client_kwargs or {}))
    try:
        return cast(Image, client.client.images.get(image_id))
    except ImageNotFound:
        return cast(Image, client.client.images.pull(image_id))


def copy_files_to_container(container: Container, host_path: Path, container_path: Path) -> None:
    """Copies a folder or a file from the host to the container."""
    tar_stream = io.BytesIO()
    with tarfile.open(fileobj=tar_stream, mode="w") as tar:
        if host_path.is_dir():
            for root, _, files in os.walk(host_path):
                for file in files:
                    file_path = Path(root) / file
                    arcname = os.path.relpath(file_path, host_path)
                    tar.add(file_path, arcname=arcname)
        else:
            tar.add(host_path, arcname=host_path.name)
    tar_stream.seek(0)
    container.put_archive(path=container_path, data=tar_stream)


def copy_files_from_container(container: Container, container_path: Path, host_path: Path) -> None:
    """Copies a folder or a file from the container to the host."""
    tar_stream, _ = container.get_archive(container_path)
    with tarfile.open(fileobj=io.BytesIO(b"".join(tar_stream))) as tar:
        tar.extractall(path=host_path)  # nosec: B202


def get_available_port() -> int:
    """Returns a random available port on the host."""
    with socket.socket() as sock:
        sock.bind(("", 0))
        return int(sock.getsockname()[1])


def get_current_ip_address() -> str:
    """Returns the current IP address of the host."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.connect(("8.8.8.8", 80))
        return str(sock.getsockname()[0])


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
