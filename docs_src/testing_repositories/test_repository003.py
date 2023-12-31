import uuid
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from types_aiobotocore_dynamodb import DynamoDBClient

from .create_customers_table import create_customers_table
from .domain001 import Customer
from .repository003 import DynamoDBCustomerRepository


@pytest_asyncio.fixture()
async def repository(moto_dynamodb_client: DynamoDBClient) -> AsyncGenerator[DynamoDBCustomerRepository, None]:
    table_name = f"autotest-{uuid.uuid4()}-customers"
    await create_customers_table(moto_dynamodb_client, table_name)
    yield DynamoDBCustomerRepository(moto_dynamodb_client, table_name)
    await moto_dynamodb_client.delete_table(TableName=table_name)


# --8<-- [start:tests]
@pytest.mark.asyncio()
async def test_save_customer(repository: DynamoDBCustomerRepository) -> None:
    # Arrange
    customer = Customer.create(name="John Doe", email="john.doe@example.com")

    # Act
    await repository.save(customer)

    # Assert
    assert await repository.get(customer.id) == customer


# --8<-- [end:tests]
