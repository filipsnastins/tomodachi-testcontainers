# --8<-- [start:fixtures]
import uuid
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from types_aiobotocore_dynamodb import DynamoDBClient

from .create_customers_table import create_customers_table
from .domain002 import (
    Customer,
    CustomerEmailAlreadyExistsError,
    CustomerIdentifierAlreadyExistsError,
    CustomerNotFoundError,
)
from .ports import CustomerRepository
from .repository006 import DynamoDBCustomerRepository, InMemoryRepository


@pytest_asyncio.fixture()
async def dynamodb_repository(moto_dynamodb_client: DynamoDBClient) -> AsyncGenerator[DynamoDBCustomerRepository, None]:
    table_name = f"autotest-{uuid.uuid4()}-customers"
    await create_customers_table(moto_dynamodb_client, table_name)
    yield DynamoDBCustomerRepository(moto_dynamodb_client, table_name)
    await moto_dynamodb_client.delete_table(TableName=table_name)


@pytest.fixture()
def fake_repository() -> InMemoryRepository:
    return InMemoryRepository([])


@pytest.fixture(params=["dynamodb", "fake"])
def repository(
    request: pytest.FixtureRequest,
    dynamodb_repository: DynamoDBCustomerRepository,
    fake_repository: InMemoryRepository,
) -> Generator[CustomerRepository, None, None]:
    if request.param == "dynamodb":
        yield dynamodb_repository
    elif request.param == "fake":
        yield fake_repository
    else:
        raise NotImplementedError


# --8<-- [end:fixtures]


# --8<-- [start:tests]
@pytest.mark.asyncio()
async def test_save_customer(repository: CustomerRepository) -> None:
    customer = Customer.create(name="John Doe", email="john.doe@example.com")

    await repository.save(customer)

    assert await repository.get(customer.id) == customer


@pytest.mark.asyncio()
async def test_customer_not_found(repository: CustomerRepository) -> None:
    with pytest.raises(CustomerNotFoundError, match="123456"):
        await repository.get("123456")


@pytest.mark.asyncio()
async def test_customer_id_should_be_unique(repository: CustomerRepository) -> None:
    customer_id = str(uuid.uuid4())
    customer_1 = Customer(id=customer_id, name="John Doe", email="john.doe@example.com")
    customer_2 = Customer(id=customer_id, name="Mary Doe", email="mary.doe@example.com")
    await repository.save(customer_1)

    with pytest.raises(CustomerIdentifierAlreadyExistsError, match=customer_id):
        await repository.save(customer_2)


@pytest.mark.asyncio()
async def test_customer_email_should_be_unique(repository: CustomerRepository) -> None:
    customer_1 = Customer.create(name="John Doe", email="john.doe@example.com")
    customer_2 = Customer.create(name="John Doe", email="john.doe@example.com")
    await repository.save(customer_1)

    with pytest.raises(CustomerEmailAlreadyExistsError, match="john.doe@example.com"):
        await repository.save(customer_2)


# --8<-- [end:tests]
