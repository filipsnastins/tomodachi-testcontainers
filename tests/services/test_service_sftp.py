import tempfile
import uuid
from typing import AsyncGenerator, Generator, cast

import asyncssh
import httpx
import pytest
import pytest_asyncio

from tomodachi_testcontainers import SFTPContainer, TomodachiContainer


@pytest.fixture(scope="module")
def tomodachi_container(
    testcontainer_image: str, sftp_container: SFTPContainer
) -> Generator[TomodachiContainer, None, None]:
    with (
        TomodachiContainer(testcontainer_image, http_healthcheck_path="/health")
        .with_env("SFTP_HOST", sftp_container.get_internal_conn_details().host)
        .with_env("SFTP_PORT", str(sftp_container.get_internal_conn_details().port))
        .with_env("SFTP_USERNAME", "userssh")
        .with_env("SFTP_PRIVATE_KEY", sftp_container.authorized_private_key.export_private_key().decode())
        .with_env("SFTP_KNOWN_HOST", sftp_container.get_internal_known_host())
        .with_command("coverage run -m tomodachi run src/sftp.py --production")
    ) as container:
        yield cast(TomodachiContainer, container)


@pytest_asyncio.fixture(scope="module")
async def http_client(tomodachi_container: TomodachiContainer) -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(base_url=tomodachi_container.get_external_url()) as client:
        yield client


@pytest.mark.asyncio()
async def test_file_not_found(http_client: httpx.AsyncClient) -> None:
    response = await http_client.get("/file/not-exists.txt")

    assert response.status_code == 404
    assert response.json() == {"error": "FILE_NOT_FOUND"}


@pytest.mark.asyncio()
async def test_upload_and_read_file(http_client: httpx.AsyncClient, userssh_sftp_client: asyncssh.SFTPClient) -> None:
    filename = f"{uuid.uuid4()}.txt"
    with tempfile.NamedTemporaryFile() as f:
        f.write(b"Hello, World!")
        f.seek(0)
        await userssh_sftp_client.put(f.name, f"upload/{filename}")

    response = await http_client.get(f"/file/{filename}")

    assert response.status_code == 200
    assert response.json() == {"content": "Hello, World!"}
