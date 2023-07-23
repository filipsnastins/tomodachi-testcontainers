import tempfile
from typing import AsyncGenerator, Generator, cast

import asyncssh
import httpx
import pytest
import pytest_asyncio
from docker.models.images import Image as DockerImage

from tomodachi_testcontainers.containers import TomodachiContainer
from tomodachi_testcontainers.containers.sftp import SFTPContainer
from tomodachi_testcontainers.utils import get_available_port


@pytest.fixture()
def service_sftp_container(
    tomodachi_image: DockerImage, sftp_container: SFTPContainer
) -> Generator[TomodachiContainer, None, None]:
    with (
        TomodachiContainer(image=str(tomodachi_image.id), edge_port=get_available_port())
        .with_env("SFTP_HOST", sftp_container.get_internal_conn_details().host)
        .with_env("SFTP_PORT", str(sftp_container.get_internal_conn_details().port))
        .with_env("SFTP_USERNAME", "userssh")
        .with_env("SFTP_PRIVATE_KEY", sftp_container.authorized_private_key.export_private_key().decode())
        .with_env("SFTP_KNOWN_HOST", sftp_container.get_internal_known_host())
        .with_command("tomodachi run src/sftp.py --production")
    ) as container:
        yield cast(TomodachiContainer, container)


@pytest_asyncio.fixture()
async def http_client(service_sftp_container: TomodachiContainer) -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(base_url=service_sftp_container.get_external_url()) as client:
        yield client


@pytest.mark.asyncio()
async def test_file_not_found(http_client: httpx.AsyncClient) -> None:
    response = await http_client.get("/file/not-exists.txt")

    assert response.status_code == 404
    assert response.json() == {
        "error": "File not found",
        "_links": {
            "self": {"href": "/file/not-exists.txt"},
        },
    }


@pytest.mark.asyncio()
async def test_upload_and_read_file(http_client: httpx.AsyncClient, userssh_sftp_client: asyncssh.SFTPClient) -> None:
    with tempfile.NamedTemporaryFile() as f:
        f.write(b"Hello, World!")
        f.seek(0)

        await userssh_sftp_client.put(f.name, "upload/hello-world.txt")

    response = await http_client.get("/file/hello-world.txt")

    assert response.status_code == 200
    assert response.json() == {
        "content": "Hello, World!",
        "_links": {
            "self": {"href": "/file/hello-world.txt"},
        },
    }
