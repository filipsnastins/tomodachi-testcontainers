# Testing Repositories

The [Repository pattern](https://martinfowler.com/eaaCatalog/repository.html) is an abstraction over the data storage layer.
It wraps database operations in an interface and hides the complexity and mechanics of the database.
The domain layer uses the Repository to query and save domain objects.
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

```py title="customers/domain.py", hl_lines="7-9 12"
--8<-- "docs_src/testing_repositories/domain001.py"
```

When you're querying for an existing object, e.g., by customer identifier or email address, the object is
_reconstructed_ from existing data from a datastore. When the data layer is separated from the domain layer,
the Repository is responsible for reconstructing the objects.
The domain layer provides an interface for object reconstruction - the object constructor method (`__init__`).

To create a new, unique customer, e.g., when a user registers in your application, we'll use the _new object creation_ method - `create`.
The `create` method requires the necessary data in the input arguments to create a new customer - `name` and `email`.
Unlike `__init__`, the `create` method doesn't require the `id`; the new random `uuid` is generated inside the `create` method.
Therefore, the _new object creation_ method encapsulates the business rules of new object creation -
in this example, the `Customer.id` generation - and offloads this responsibility from the data layer.

We'll see how separating the object reconstruction from the new object creation is useful when implementing a sample Repository.

### Implementing DynamoDB Repository

In this example, we'll use [AWS DynamoDB](https://aws.amazon.com/pm/dynamodb/) to implement `DynamoDBCustomerRepository`.
The sample Repository has two methods - constructor (`__init__`) and `save` method.

The constructor takes two dependencies - `DynamoDBClient` and `table_name`. Explicitly passing the dependencies increases flexibility -
the Repository will be easy to test and configure in the production code,
as the next section where we'll write Repository tests will show.
The `save` method persists a `Customer` object in the database; its current implementation is the simplest version.

```py title="customers/dynamodb_repository.py" hl_lines="7 11"
--8<-- "docs_src/testing_repositories/dynamodb_repository001.py"
```

## Testing with a production-like database

As we learned in the [Testing Databases](testing-databases.md), we want to test the Repository
as close to the production setup as possible.
To test DynamoDB, we'll use [Moto AWS service mocks](https://github.com/getmoto/moto). An alternative is using a real AWS account -
that will make the tests most accurate but slower and more complicated to configure securely due to permission and account management - if we're not careful, we can accidentally run the tests on a production AWS account.
Service mocks like [Moto](https://github.com/getmoto/moto) or [LocalStack](https://www.localstack.cloud/)
are good enough for most use cases.

To test the Repository, we need to instantiate it with `DynamoDBClient` and `table_name`.
We'll get the `DynamoDBClient` from the Tomodachi Testcontainers library with the `moto_dynamodb_client` fixture.
The fixture will automatically start `MotoContainer`.
For the `table_name`, any string value will suffice - we're using a value with
a random `uuid` suffix as a namespace to avoid table name clashes during tests.

!!! success "Dependency injection increases testability."

    Being able to pass a different `DynamoDBClient` to the Repository in tests is powerful -
    it makes the code testable and explicit about its dependencies.
    To configure the Repository in the production code, we'd create a new `DynamoDBClient`
    instance with configuration values from the environment variables.

The first test `test_save_customer` creates a new `Customer` object and calls the `save` method to persist it in the database.
The assertion is missing for now - we'll look into what to assert in the next section.

```py title="tests/test_dynamodb_repository.py" hl_lines="14 17 22"
--8<-- "docs_src/testing_repositories/test_dynamodb_repository001.py"
```

For the example completeness, the function below creates a new DynamoDB table.

```py title="tests/create_customers_table.py"
--8<-- "docs_src/testing_repositories/create_customers_table001.py"
```

## Test the interface, not the implementation

## Testing other Repository implementations with the same test suite

## Tying it all together with the Ports & Adapters pattern

TODO link to a more general pattern - ports and adapters

<figure markdown>
  ![Container Diagram - Application with Relational Database](../architecture/c4/level_2_container/01_app_with_relational_db.png)
</figure>

<figure markdown>
  ![Component Diagram - Application with Relational Database](../architecture/c4/level_3_component/01_app_with_relational_db.png)
</figure>

## References

- <https://martinfowler.com/eaaCatalog/repository.html>
- <https://martinfowler.com/bliki/DomainDrivenDesign.html>
- <https://www.cosmicpython.com/book/chapter_02_repository.html>
- <https://ddd.mikaelvesavuori.se/tactical-ddd/repositories>
- <https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/infrastructure-persistence-layer-design>
