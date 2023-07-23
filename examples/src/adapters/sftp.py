import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import asyncssh


@asynccontextmanager
async def get_sftp_client() -> AsyncGenerator[asyncssh.SFTPClient, None]:
    client_keys = asyncssh.import_private_key(os.environ.get("SFTP_PRIVATE_KEY", ""))
    known_hosts = asyncssh.SSHKnownHosts(os.environ.get("SFTP_KNOWN_HOST", ""))
    async with asyncssh.connect(
        host=os.environ.get("SFTP_HOST"),
        port=int(os.environ.get("SFTP_PORT", "")),
        username=os.environ.get("SFTP_USERNAME"),
        client_keys=client_keys,
        known_hosts=known_hosts,
    ) as ssh_conn:
        async with ssh_conn.start_sftp_client() as sftp_client:
            yield sftp_client
