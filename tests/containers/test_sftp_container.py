import tempfile
import uuid

import asyncssh
import pytest


@pytest.mark.asyncio
async def test_sftp_container__authenticate_with_password(userpass_sftp_client: asyncssh.SFTPClient) -> None:
    filename = f"{uuid.uuid4()}.txt"

    with tempfile.NamedTemporaryFile() as f:
        f.write(b"Hello, World!")
        f.seek(0)
        await userpass_sftp_client.put(f.name, f"upload/{filename}")

    listdir = await userpass_sftp_client.listdir("upload")
    assert set(listdir) == {".", "..", filename}


@pytest.mark.asyncio
async def test_sftp_container__authenticate_with_ssh_keys(userssh_sftp_client: asyncssh.SFTPClient) -> None:
    filename = f"{uuid.uuid4()}.txt"

    cwd = await userssh_sftp_client.getcwd()
    assert cwd == "/"

    with tempfile.NamedTemporaryFile() as f:
        f.write(b"Hello, World!")
        f.seek(0)
        await userssh_sftp_client.put(f.name, f"upload/{filename}")

    listdir = await userssh_sftp_client.listdir("upload")
    assert set(listdir) == {".", "..", filename}
