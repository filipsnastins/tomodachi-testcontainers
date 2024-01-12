import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import asyncssh


@asynccontextmanager
async def create_sftp_client() -> AsyncGenerator[asyncssh.SFTPClient, None]:
    client_keys = asyncssh.import_private_key(os.getenv("SFTP_PRIVATE_KEY", ""))
    known_hosts = asyncssh.SSHKnownHosts(os.getenv("SFTP_KNOWN_HOST", ""))
    async with asyncssh.connect(
        host=os.getenv("SFTP_HOST"),
        port=int(os.getenv("SFTP_PORT", "22")),
        username=os.getenv("SFTP_USERNAME"),
        client_keys=client_keys,
        known_hosts=known_hosts,
    ) as ssh_conn:
        async with ssh_conn.start_sftp_client() as sftp_client:
            yield sftp_client
