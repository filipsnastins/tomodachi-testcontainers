# Testing Repositories

The [Repository pattern](https://martinfowler.com/eaaCatalog/repository.html) is an abstraction over the data storage layer.
It wraps database operations in an interface and hides the complexity and mechanics of the database.
The domain layer uses the Repository to query and persist domain objects.
From the domain layer point of view, the Repository's interface looks like an in-memory domain object collection.

The Repository's responsibility is object retrieval and persistence - it contains no business logic.
Therefore, all business logic resides in the domain objects, not the data layer.
This separation of responsibilities makes testing and reasoning about the core application's behavior easier.
In tests, you'll provide an in-memory object to the domain logic you want to test
without being burdened by the test data setup through the production database.

The Repository pattern is described in detail in the [PoEAA](https://martinfowler.com/eaaCatalog/repository.html)
and [DDD](https://martinfowler.com/bliki/DomainDrivenDesign.html).
Other great resources I know of are:
[cosmicpython book's chapter on Repositories](https://www.cosmicpython.com/book/chapter_02_repository.html),
[Repositories for DDD on AWS](https://ddd.mikaelvesavuori.se/tactical-ddd/repositories),
and [designing persistence layer with .NET example](https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/infrastructure-persistence-layer-design).

The following sections will explore testing Repositories separately from the rest of the application.

## Implementing a simple Repository

The Repository implementation will differ depending on the database technology
(relational, NoSQL, file store, etc.) and the framework (ORM, datastore client library, etc.).
The most important part is not exposing the underlying technology in the Repository's interface.

### Implementing domain object

Before exploring how to test a Repository, we must create a domain object that the Repository will save and query.
We'll use a `Customer` object as an example.

There are two ways to create a new `Customer` object instance -
with the default constructor (auto-generated with `@dataclass`) or a `create` factory method.
The former is used for _object reconstruction_ and the latter for _new object creation_.

```py title="customers/domain.py" hl_lines="7-9 12"
--8<-- "docs_src/testing_repositories/domain001.py"
```

When you're querying an existing object, e.g., by customer identifier or email address, the object is
_reconstructed_ from existing data from a datastore. When the data layer is separated from the domain layer,
the Repository is responsible for reconstructing the objects.
The domain layer provides an interface for object reconstruction - the object constructor method (`__init__`).

To create a new, unique customer, e.g., when a user registers in your application, we'll use the _new object creation_ method - `create`.
The `create` method requires the data to create a new customer - `name` and `email`.
Unlike `__init__`, the `create` method doesn't require the `id`; the new random `uuid` is generated inside the `create` method.
Therefore, the _new object creation_ method encapsulates the rules of a new object creation -
in this example, the `Customer.id` generation - and offloads this responsibility from the data layer.

We'll see how separating the object reconstruction from the new object creation is useful when implementing a sample Repository.

### Implementing DynamoDB Repository

In this example, we'll use [AWS DynamoDB](https://aws.amazon.com/pm/dynamodb/) to implement `DynamoDBCustomerRepository`.
The sample Repository has two methods - constructor (`__init__`) and `save` method.

The constructor takes two dependencies - `DynamoDBClient` and `table_name`. Explicitly passing the dependencies increases flexibility -
the Repository will be easy to configure in tests and in the production code, as we'll see in the following sections.
The `save` method persists a `Customer` object in the database; its implementation is the minimal working version to showcase the example.

```py title="adapters/repository.py" hl_lines="7 11"
--8<-- "docs_src/testing_repositories/repository001.py"
```

## Testing with a production-like database

As we learned in the [Testing Databases](testing-databases.md), we want to test the Repository with a production-like database.
To test the DynamoDB Repository, we'll use [Moto AWS service mocks](https://github.com/getmoto/moto).
An alternative is using a real AWS account - that will make the tests accurate but slower
and more complicated to configure securely due to permission and account management -
if we're not careful, we can accidentally run the tests on a production AWS account.
Service mocks like [Moto](https://github.com/getmoto/moto) or [LocalStack](https://www.localstack.cloud/) are good enough for most use cases.

To test the Repository, we need to instantiate it with `DynamoDBClient` and `table_name`.
We'll get the `DynamoDBClient` from the Tomodachi Testcontainers library with the `moto_dynamodb_client` fixture.
The fixture will automatically start `MotoContainer`. For the `table_name`, any string value will suffice;
the example is using a value with a random `uuid` suffix as a namespace to avoid table name clashes during tests.

!!! success "Dependency injection increases testability"

    Being able to pass a different `DynamoDBClient` to the Repository in tests is powerful -
    it makes the code testable and explicit about its dependencies.
    To configure the Repository in the production code, we'd create a new `DynamoDBClient`
    instance with configuration values from the environment variables.

The first test `test_save_customer` creates a new `Customer` object and calls the `save` method to persist it in the database.
The assertion is missing for now - we'll look into what to assert in the next section.

```py title="tests/test_repository.py" hl_lines="14 17 22"
--8<-- "docs_src/testing_repositories/test_repository001.py"
```

For the example completeness, the function below creates a new DynamoDB table.

```py title="tests/create_customers_table.py"
--8<-- "docs_src/testing_repositories/create_customers_table.py"
```

## Test the interface, not the implementation

To test that the Repository has saved an object in a database, we can query the database and assert that the data is stored correctly.
This approach has a significant drawback - the tests know about the Repository's implementation details,
such as how and where the data is stored. As more functionality is added to the Repository, the tests
will become brittle, lengthy, and difficult to maintain.

```py title="tests/test_repository.py" hl_lines="10-19"
--8<--
docs_src/testing_repositories/test_repository002.py:tests
--8<--
```

To test the Repository, verify its behavior by calling only its public API - _test the interface, not the implementation_.
The intent of the `test_save_customer` is to assert that the `Customer` object is saved to the Repository -
that it's possible to retrieve it back from the Repository and that its data is the same.
This way, the tests are not concerned with the database's internal data structure,
which can now change independently without breaking the tests.

The `DynamoDBCustomerRepository.get` reconstructs a customer's object from existing data from the database.

```py title="adapters/repository.py" hl_lines="22"
class DynamoDBCustomerRepository:
    ...

--8<--
docs_src/testing_repositories/repository003.py:get
--8<--
```

!!! success "Repository's public API round-trip testing helps to avoid testing implementation details"

    You can think of the pattern of saving an object and querying it in the same test as a "round-trip" test.
    The same test verifies a complete cycle of a domain object persistence - saved in the datastore and retrieved back.
    The example doesn't include updating the domain object, but the same idea applies -
    create (arrange), update (act), query (assert).

To test a negative case when the `Customer` is not found in the Repository,
we can test that the `get` method raises an exception.
The current Repository implementation will throw the `KeyError` because the `Item` key will
not exist in the DynamoDB `GetItem` API response. This test has the same problem as the first example -
it asserts on the implementation detail - `KeyError`.

The test shouldn't care if the internal data structure is a dictionary that throws the `KeyError` when the dictionary key is not found.
In addition, the `KeyError` might not necessarily mean that the customer is not found in the Repository.
If the Repository has a bug and is not saving the customer's object field, the same error will be raised
when trying to access the unsaved field, e.g., `email=item["Email"]["S"]`. In this case, the error handling code
catching the `KeyError` will always treat it as the "customer not found" case and return misleading results to the application's end user.

```py title="tests/test_repository.py" hl_lines="3"
--8<--
docs_src/testing_repositories/test_repository004.py:tests
--8<--
```

To hide the exception's implementation details, we introduce a new _domain exception_ - `CustomerNotFoundError` -
to identify and handle the error unambiguously.
The domain exception is part of the Repository's public API - when a customer with a given `customer_id` is not found,
the `CustomerNotFoundError` is raised.
All Repository's implementations must adhere to this public API or contract, regardless of the underlying database technology.

```py title="adapters/repository.py" hl_lines="9-11"
class DynamoDBCustomerRepository:
    ...

--8<--
docs_src/testing_repositories/repository005.py:get
--8<--
```

```py title="tests/test_repository.py" hl_lines="6"
from .repository005 import CustomerNotFoundError


--8<--
docs_src/testing_repositories/test_repository005.py:tests
--8<--
```

## Implementing a fake Repository

The database implementation details obscure the intent of the application's business logic, so we have hidden
the details behind the Repository's interface - a contract between the application's domain layer and persistence layer.

To further ease domain layer testing, instead of using the production `DynamoDBCustomerRepository`,
we can replace it with an in-memory fake Repository. The fake Repository will store the data in an in-memory dictionary.
The in-memory version is unsuitable for real-world use because the data is lost on application shutdown, and the Repository is not scalable.
However, if the fake Repository behaves the same as the real one, it's a good choice for unit testing, prototyping, and demos.
There's no database or Testcontainers to manage, and the tests will be fast.

```py title="adapters/repository.py"
--8<--
docs_src/testing_repositories/repository006.py:in_memory_repository
--8<--
```

The in-memory repository is useful not just for testing; when modeling a complex and unknown domain,
you can postpone the decision of which database technology to use and focus the development efforts on the problem domain.
By using the Repository with a clean interface, you'll be able to quickly evolve the domain layer without being slowed down
by the accidental complexities of a production database - mapping domain objects to the datastore format and back,
managing schema and data migration, handling infrastructure errors, etc.
You can better commit to a specific technology when the problem domain is more explored and apparent with how the data is queried and used.

!!! success "Let the problem domain drive your technological choices"

    By focusing the development on the problem domain first and keeping the infrastructure concerns on the periphery,
    later, you can make informed choices of which specific technologies are better suited for your needs.
    It's a significant benefit of the broader [Ports & Adapters](./ports-and-adapters.md) pattern -
    hiding accidental complexity of low-level components.
    The Ports & Adapters apply to all systems - databases, file stores, external services, message brokers, etc.

## Testing other Repository implementations with the same test suite

To ensure that the in-memory Repository works, we must test it with the same test suite as the production Repository.
Since the interface is the same and tests are [testing the interface, not the implementation](#test-the-interface-not-the-implementation),
the test suite doesn't care which Repository it's given, in-memory, DynamoDB, PostgreSQL, AWS S3, etc., as long as the behavior is the same.
Knowing this property, we could have implemented the in-memory repository and its tests before the DynamoDB version.

To reuse the same test suite for testing multiple Repository versions, we'll use `pytest` parametrized fixtures.
Any other popular test runner should have a similar concept.
We'll define two fixtures, `dynamodb_repository` and `fake_repository`, and use them in the generic `repository` fixture.
The `repository` fixture is parametrized; when a test case uses the fixture, it will be run twice -
with `dynamodb` and `fake` parameters. Depending on the passed parameter, the fixture will return `DynamoDBCustomerRepository` or `InMemoryRepository`.

```py title="tests/test_repository.py" hl_lines="20 28 33"
--8<--
docs_src/testing_repositories/test_repository006.py:fixtures
--8<--
```

The tests use the generic `repository` fixture instead of a specific implementation and are run twice -
with `DynamoDBCustomerRepository` and `InMemoryRepository`.

```py title="tests/test_repository.py" hl_lines="1 5 14 20 31"
from .ports006 import CustomerRepository


--8<--
docs_src/testing_repositories/test_repository006.py:tests
--8<--
```

For the type hint, the repository tests use the generic Repository's protocol - the "Port" part of the "Ports & Adapters" pattern.

```py title="customers/ports.py"
--8<-- "docs_src/testing_repositories/ports006.py"
```

<figure markdown>
  ![Testing other Repository implementations with the same test suite](../images/testing-multiple-repositories-with-the-same-test-suite.png)
  <figcaption>Running the same test suite with different pytest fixture implementations.</figcaption>
</figure>

## Decoupling and Testing Infrastructure Layer with Ports & Adapters Pattern

This section used the Repository pattern to decouple the persistence layer from the domain layer.
The Repository pattern is a specific application for another, more general pattern -
[Ports & Adapters](<https://en.wikipedia.org/wiki/Hexagonal_architecture_(software)>).
The Ports & Adapters pattern helps decouple all sorts of components, not just databases.
The following section [Decoupling and Testing Infrastructure Layer with Ports & Adapters Pattern](./ports-and-adapters.md)
describes in more detail the applications of Ports & Adapters,
and how Testcontainers help to implement and test the "Adapters" part of the pattern.

The diagrams below ([C4](https://c4model.com/)) showcase how the Ports & Adapters pattern helps to implement the example Repository.

<figure markdown>
  ![Container Diagram - Application with DynamoDB Database](../architecture/c4/level_2_container/02_app_with_dynamodb.png)
</figure>

Ports are the interfaces of our infrastructure components; they reside in the domain layer.
Adapters or the Infrastructure layer implement the Ports.
There are two implementations - in-memory Repository and DynamoDB Repository.
Testcontainers help to test the DynamoDB Repository in a production-like environment by provisioning AWS service mocks, e.g., LocalStack.

The diagram shows that all dependencies (arrows) flow towards the domain layer. It means the domain layer doesn't depend on other
infrastructure components. It makes the domain layer testable in isolation and makes it easier to understand the code.

<figure markdown>
  ![Container Diagram - Application with DynamoDB Database](../architecture/c4/level_3_component/02_app_with_dynamodb.png)
</figure>

## References

- <https://martinfowler.com/eaaCatalog/repository.html>
- <https://martinfowler.com/bliki/DomainDrivenDesign.html>
- <https://www.cosmicpython.com/book/chapter_02_repository.html>
- <https://ddd.mikaelvesavuori.se/tactical-ddd/repositories>
- <https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/infrastructure-persistence-layer-design>
- <https://en.wikipedia.org/wiki/Hexagonal_architecture_(software)>
