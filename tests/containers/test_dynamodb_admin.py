from typing import Generator, cast

import httpx
import pytest

from tomodachi_testcontainers import DynamoDBAdminContainer, MotoContainer
from tomodachi_testcontainers.utils import get_available_port


# Copy and paste this fixture to your project if you need to do some exploratory testing of the DynamoDB state
@pytest.fixture(scope="module", autouse=True)
def dynamodb_admin_container(moto_container: MotoContainer) -> Generator[DynamoDBAdminContainer, None, None]:
    with DynamoDBAdminContainer(
        dynamo_endpoint=moto_container.get_internal_url(),
        edge_port=get_available_port(),
    ) as container:
        yield cast(DynamoDBAdminContainer, container)


@pytest.mark.asyncio()
async def test_dynamodb_admin_container_starts(dynamodb_admin_container: DynamoDBAdminContainer) -> None:
    async with httpx.AsyncClient(base_url=dynamodb_admin_container.get_external_url()) as client:
        response = await client.get("/")

    assert response.status_code == 200
