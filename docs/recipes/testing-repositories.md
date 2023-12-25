# Testing Repositories

The [Repository pattern](https://martinfowler.com/eaaCatalog/repository.html) is an abstraction over the data storage layer.
It wraps database operations in an interface and hides the complexity and mechanics of the database.
The domain layer uses the Repository to query and save domain objects.
From the domain layer point of view, the Repository's interface looks like an in-memory domain object collection.

The Repository's responsibility is object retrieval and persistence - it contains no business logic.
Therefore, all business logic resides in the domain objects, not the data layer.
This separation of responsibilities makes testing and reasoning about the core application's behavior easier.

The Repository pattern application is described in detail in the [PoEAA](https://martinfowler.com/eaaCatalog/repository.html)
and [DDD](https://martinfowler.com/bliki/DomainDrivenDesign.html).
Other great resources I know of are:
[cosmicpython book's chapter on Repositories](https://www.cosmicpython.com/book/chapter_02_repository.html),
[Repositories for DDD on AWS](https://ddd.mikaelvesavuori.se/tactical-ddd/repositories),
and [designing persistence layer with .NET example](https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/infrastructure-persistence-layer-design).

The following sections will explore the testing aspect of the Repositories - how to test the Repository separately from the rest of the application.

## Implementing a simple Repository

### Implementing domain object

Before exploring how to test a Repository, we must create a domain object that the Repository will save and query.
We'll use a `Customer` object as an example.

There are two ways to create a new `Customer` object instance -
with the default constructor (`__init__`) auto-generated with `@dataclass` or with a static method `create`.
The former is used for _object reconstruction_ and the latter for _new object creation_.

```py title="customers/domain.py", hl_lines="7-9 12"
--8<-- "docs_src/testing_repositories/domain001.py"
```

When you're querying for an existing object, e.g., by customer identifier or email address, the object is
_reconstructed_ from existing data from a datastore. When the data layer is separated from the domain layer with the Repository pattern,
the Repository is responsible for reconstructing the objects.
The domain layer provides an interface for object reconstruction - the `__init__` method on the `Customer` object.

To create a new, unique customer, e.g., when a user registers in your application, we'll use the _new object creation_ method - `create`.
The `create` method requires the necessary data in the input arguments to create a new customer - `name` and `email`.
Unlike `__init__`, the `create` method doesn't require the `id`; the new random `uuid` is generated in the `create` method.
Therefore, the _new object creation_ method encapsulates the business rules of new object creation -
in this example, the `Customer.id` generation - and offloads this responsibility from the data layer.

We'll see how separating the object reconstruction from the new object creation is useful when implementing a sample Repository.

### Implementing DynamoDB Repository

```py title="customers/dynamodb_repository.py"
--8<-- "docs_src/testing_repositories/dynamodb_repository001.py"
```

## Testing with a production-like database

```py title="tests/test_dynamodb_repository.py"
--8<-- "docs_src/testing_repositories/test_dynamodb_repository001.py"
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
