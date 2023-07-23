import os
from typing import AsyncGenerator, Generator

import asyncssh
import pytest
import pytest_asyncio

from tomodachi_testcontainers.containers import SFTPContainer
from tomodachi_testcontainers.utils import get_available_port


@pytest.fixture(scope="session")
def sftp_container() -> Generator[SFTPContainer, None, None]:
    image = os.environ.get("SFTP_TESTCONTAINER_IMAGE_ID", "atmoz/sftp:latest")
    with SFTPContainer(image=image, edge_port=get_available_port()) as container:
        yield container


@pytest_asyncio.fixture()
async def userpass_sftp_client(sftp_container: SFTPContainer) -> AsyncGenerator[asyncssh.SFTPClient, None]:
    conn_details = sftp_container.get_external_conn_details()
    async with asyncssh.connect(
        host=conn_details.host,
        port=conn_details.port,
        username="userpass",
        password="pass",  # nosec: B106
        known_hosts=sftp_container.get_known_hosts(),
    ) as ssh_conn:
        async with ssh_conn.start_sftp_client() as sftp_client:
            yield sftp_client


@pytest_asyncio.fixture()
async def userssh_sftp_client(sftp_container: SFTPContainer) -> AsyncGenerator[asyncssh.SFTPClient, None]:
    conn_details = sftp_container.get_external_conn_details()
    async with asyncssh.connect(
        host=conn_details.host,
        port=conn_details.port,
        username="userssh",
        client_keys=sftp_container.authorized_private_key,
        known_hosts=sftp_container.get_known_hosts(),
    ) as ssh_conn:
        async with ssh_conn.start_sftp_client() as sftp_client:
            yield sftp_client
