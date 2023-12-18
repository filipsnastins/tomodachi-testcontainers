import os
from typing import Any, Optional

from .common import WebContainer


class DynamoDBAdminContainer(WebContainer):
    def __init__(
        self,
        dynamo_endpoint: str,
        image: str = "aaronshaf/dynamodb-admin:latest",
        internal_port: int = 8001,
        edge_port: int = 8001,
        region_name: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            image=image,
            internal_port=internal_port,
            edge_port=edge_port,
            http_healthcheck_path="/",
            **kwargs,
        )

        self.region_name = region_name or os.getenv("AWS_DEFAULT_REGION") or "us-east-1"
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID") or "testing"  # nosec: B105
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY") or "testing"  # nosec: B105

        self.with_env("AWS_REGION", self.region_name)
        self.with_env("AWS_ACCESS_KEY_ID", self.aws_access_key_id)
        self.with_env("AWS_SECRET_ACCESS_KEY", self.aws_secret_access_key)

        self.with_env("DYNAMO_ENDPOINT", dynamo_endpoint)

    def log_message_on_container_start(self) -> str:
        return f"DynamoDB Admin: http://localhost:{self.edge_port}"
