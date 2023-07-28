import tempfile

import asyncssh
import pytest

from tomodachi_testcontainers.containers import SFTPContainer


@pytest.mark.asyncio()
async def test_sftp_container__authenticate_with_password(sftp_container: SFTPContainer) -> None:
    async with asyncssh.connect(
        host="localhost",
        port=sftp_container.edge_port,
        username="userpass",
        password="pass",
        known_hosts=sftp_container.get_known_hosts(),
    ) as conn:
        async with conn.start_sftp_client() as sftp:
            cwd = await sftp.getcwd()
            assert cwd == "/"

            await sftp.chdir("upload")
            cwd = await sftp.getcwd()
            assert cwd == "/upload"

            with tempfile.NamedTemporaryFile() as f:
                f.write(b"Hello, World!")
                f.seek(0)

                await sftp.put(f.name, "hello-world.txt")

            listdir = await sftp.listdir(".")
            assert set(listdir) == {".", "..", "hello-world.txt"}


@pytest.mark.asyncio()
async def test_sftp_container__authenticate_with_ssh_keys(sftp_container: SFTPContainer) -> None:
    async with asyncssh.connect(
        host="localhost",
        port=sftp_container.edge_port,
        username="userssh",
        client_keys=sftp_container.authorized_private_key,
        known_hosts=sftp_container.get_known_hosts(),
    ) as conn:
        async with conn.start_sftp_client() as sftp:
            cwd = await sftp.getcwd()
            assert cwd == "/"

            await sftp.chdir("upload")
            cwd = await sftp.getcwd()
            assert cwd == "/upload"

            with tempfile.NamedTemporaryFile() as f:
                f.write(b"Hello, World!")
                f.seek(0)

                await sftp.put(f.name, "hello-world.txt")

            listdir = await sftp.listdir(".")
            assert set(listdir) == {".", "..", "hello-world.txt"}
