from typing import Any, NamedTuple

import asyncssh
from testcontainers.core.waiting_utils import wait_for_logs

from .common import DockerContainer

ConnectionDetails = NamedTuple("ConnectionDetails", [("host", str), ("port", int)])


class SFTPContainer(DockerContainer):
    def __init__(
        self,
        image: str = "atmoz/sftp:latest",
        internal_port: int = 22,
        edge_port: int = 2222,
        **kwargs: Any,
    ) -> None:
        super().__init__(image, **kwargs)
        self.internal_port = internal_port
        self.edge_port = edge_port
        self.with_bind_ports(self.internal_port, self.edge_port)

        self.with_command("userpass:pass:1001 userssh::1002")

        self.authorized_private_key = asyncssh.generate_private_key("ssh-ed25519")
        self.authorized_public_key = self.authorized_private_key.export_public_key().decode()

    def log_message_on_container_start(self) -> str:
        return f"SFTP server running on port: {self.edge_port}"

    def get_internal_conn_details(self) -> ConnectionDetails:
        host = self.get_container_internal_ip()
        return ConnectionDetails(host=host, port=self.internal_port)

    def get_external_conn_details(self) -> ConnectionDetails:
        host = self.get_container_host_ip()
        return ConnectionDetails(host=host, port=self.edge_port)

    def get_host_public_key(self) -> str:
        _, output = self.exec("bash -c 'cat /etc/ssh/ssh_host_ed25519_key.pub'")
        return bytes(output).decode().strip()

    def get_internal_known_host(self) -> str:
        internal = self.get_internal_conn_details()
        public_key = self.get_host_public_key()
        return f"{internal.host} {public_key}"

    def get_external_known_host(self) -> str:
        external = self.get_external_conn_details()
        public_key = self.get_host_public_key()
        return f"{external.host} {public_key}"

    def get_known_hosts(self) -> asyncssh.SSHKnownHosts:
        known_hosts = asyncssh.SSHKnownHosts()
        for known_host in [self.get_internal_known_host(), self.get_external_known_host()]:
            known_hosts.load(known_host)
        return known_hosts

    def add_authorized_key(self, username: str, uid: str, gid: str, public_key: str) -> None:
        self.exec(f"bash -c 'mkdir -p /home/{username}/.ssh'")
        self.exec(f"bash -c 'chmod 700 /home/{username}/.ssh'")
        self.exec(f"bash -c 'touch /home/{username}/.ssh/authorized_keys'")
        self.exec(f"bash -c 'chmod 600 /home/{username}/.ssh/authorized_keys'")
        self.exec(f"bash -c 'echo \"{public_key}\" >> /home/{username}/.ssh/authorized_keys'")
        self.exec(f"bash -c 'chown -R {uid}:{gid} /home/{username}/.ssh'")

    def start(self, timeout: float = 10.0) -> "SFTPContainer":
        super().start()
        wait_for_logs(self, r"Server listening on", timeout=timeout)

        self.exec("bash -c 'mkdir /home/userpass/upload && chown -R 1001:1001 /home/userpass/upload'")
        self.exec("bash -c 'mkdir /home/userpass/download && chown -R 1001:1001 /home/userpass/download'")
        self.exec("bash -c 'mkdir /home/userssh/upload && chown -R 1002:1002 /home/userssh/upload'")
        self.exec("bash -c 'mkdir /home/userssh/download && chown -R 1002:1002 /home/userssh/download'")

        self.add_authorized_key(username="userssh", uid="1002", gid="1002", public_key=self.authorized_public_key)

        return self
