import uuid
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from types_aiobotocore_dynamodb import DynamoDBClient

from .create_customers_table import create_customers_table
from .domain001 import Customer
from .repository001 import DynamoDBCustomerRepository


@pytest_asyncio.fixture(loop_scope="session")
async def repository(moto_dynamodb_client: DynamoDBClient) -> AsyncGenerator[DynamoDBCustomerRepository, None]:
    table_name = f"autotest-{uuid.uuid4()}-customers"
    await create_customers_table(moto_dynamodb_client, table_name)
    yield DynamoDBCustomerRepository(moto_dynamodb_client, table_name)
    await moto_dynamodb_client.delete_table(TableName=table_name)


# --8<-- [start:tests]
@pytest.mark.asyncio(loop_scope="session")
async def test_save_customer(repository: DynamoDBCustomerRepository, moto_dynamodb_client: DynamoDBClient) -> None:
    # Arrange
    customer = Customer.create(name="John Doe", email="john.doe@example.com")

    # Act
    await repository.save(customer)

    # Assert
    item = await moto_dynamodb_client.get_item(
        TableName=repository._table_name,
        Key={"PK": {"S": f"CUSTOMER#{customer.id}"}},
    )
    assert item["Item"] == {
        "PK": {"S": f"CUSTOMER#{customer.id}"},
        "Id": {"S": customer.id},
        "Name": {"S": "John Doe"},
        "Email": {"S": "john.doe@example.com"},
    }


# --8<-- [start:end]
