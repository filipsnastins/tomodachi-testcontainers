# Testing Databases

## Using in-memory SQLite database in tests

### Use case

If an application uses a relational database and Object-Relational Mapper (ORM) for implementing a data layer,
it's easy to replace a production database, e.g., PostgreSQL or MySQL, with an in-memory SQLite database.
SQLite does not require additional setup or dependencies, and it might seem like a convenient choice for autotests.

For example, using SQLAlchemy, set the database URL to `sqlite://` to connect to an in-memory SQLite database;
it will use the built-in Python module `sqlite3`:

```py
from sqlalchemy import create_engine

engine = create_engine("sqlite://")
```

### Drawbacks

Using SQLite in tests creates compatibility problems between the SQLite and your production database
because the two database technologies support different features and implement some SQL statements differently.

ORMs try to abstract these differences, especially different SQL flavors, but don't eliminate them.
ORMs are not designed to enable a switch from one relational database technology to another without changes to the application code.

When using SQLite for testing, the application code must only use standard features available in the SQLite and production databases.
This cuts the benefits an application can get by using unique features of a particular database technology,
potentially lowering performance and increasing the complexity of the application code.

!!! danger "Testing with SQLite does not guarantee that the application will work in production."

    Theres's no guarantee that the application that passed the tests using SQLite will work in the production environment with the production database.
    An ORM can still fail to work with the production database due to unknown differences in behavior.

## Using a production-like database in tests with Testcontainers

Autotests must give confidence that the application will work in the production environment,
so development/test/production [environment parity](https://12factor.net/dev-prod-parity) is crucial for reliable automated testing.

!!! success "Use production-like database in tests."

    Whether your application uses a relational or NoSQL database,
    use the same database technology, version, and configuration in automated tests as in your production environment.

Testconainters lets you easily create and delete a temporary database when the tests finish.

For the application to use the test database, inject the test database URL into the application configuration;
using [environment variables](https://12factor.net/config) for managing configuration is a good practice.

Below is an example of [configuring the Flask application](https://flask.palletsprojects.com/en/3.0.x/testing/) with the `PostgreSQLContainer` Testcontainer.
The `postgres_container` fixture creates a new instance of the PostgreSQL database and deletes it when tests finish.
The Flask application reads the database URL from the `DATABASE_URL` environment variable;
set it before running the [Flask application factory](https://flask.palletsprojects.com/en/3.0.x/tutorial/factory/) `create_app`.

```py
import pytest
from flask import Flask
from tomodachi_testcontainers import PostgreSQLContainer

from my_project import create_app

@pytest.fixture()
def app(monkeypatch: pytest.MonkeyPatch, postgres_container: PostgreSQLContainer) -> Flask:
    monkeypatch.setenv("DATABASE_URL", str(postgres_container.get_external_url()))
    return create_app()
```

The same approach works with other database technologies: [MongoDB](https://hub.docker.com/_/mongo), [DynamoDB](https://hub.docker.com/r/localstack/localstack/), etc.

### Improving database performance in tests

Modern databases are already fast enough to be used in automated testing -
startup time is less than a second, and database read/write performance lets you run hundreds of tests in a reasonable time.

The slowest database operation is writing data to a disk on a commit.
The test database is deleted when autotests finish, so the test data is discarded anyway.
Therefore, to increase the test database performance, disable data flush to disk and let the database store the data in faster RAM.
Read more about this technique and performance measurements in [this blog post](https://pythonspeed.com/articles/faster-db-tests/).

Most databases have a similar configuration option that disables the flush to the disk.
To disable the flush to the disk in PostgreSQL, set the `fsync` parameter to `off`:

```sh
docker run --rm -p 5432:5432 postgres:16 -c fsync=off
```

In MySQL set `innodb_flush_method=O_DIRECT_NO_FSYNC`:

```sh
docker run --rm -p 3306:3306 mysql:8 --innodb_flush_method=O_DIRECT_NO_FSYNC
```

!!! tip

    In Tomodachi Testcontainers library, database containers have `fsync` disabled by default.

## Replacing the database with fakes or mocks

The previous section described testing with a production-like database to verify that interactions
between an application and the database will work in the production environment.
However, when writing unit tests that exercise individual application components in isolation,
you might find that the database is getting in the way - test data is tedious to set up, and the database setup code obscures the intent of the test.
It might signal that the system component under test is unnecessarily tightly coupled to the database, making it difficult to test its behavior.

In this case, the system might benefit from separating the data storage layer from the business logic layer.
The [Repository pattern](https://martinfowler.com/eaaCatalog/repository.html) is an abstraction over the data storage layer.
It wraps database operations in an interface and hides the complexity and mechanics of the database.
When using the Repository pattern, the business logic doesn't directly call ORM models or database drivers to access data storage
but does so indirectly through the Repository interface.

To test the business logic without the complexity of the production database, substitute the real Repository with a fake or mock.
To ensure the data storage layer works, separately test the real Repository implementation with the production database.
That is described in the next section - [Testing Repositories](./testing-repositories.md).

To learn more about the Repository pattern use cases,
check out [cosmicpython book chapter](https://www.cosmicpython.com/book/chapter_02_repository.html) on the topic
and the [original pattern description in the PoEAA catalog](https://martinfowler.com/eaaCatalog/repository.html).

Since examples in this section focused on relational databases,
it's worth mentioning that the Repository pattern is database technology agnostic -
[see an example implementation with DynamoDB](https://ddd.mikaelvesavuori.se/tactical-ddd/repositories).

## References

- <https://12factor.net/dev-prod-parity>
- <https://12factor.net/config>
- <http://michael.robellard.com/2015/07/dont-test-with-sqllite-when-you-use.html>
- <https://pythonspeed.com/articles/faster-db-tests/>
- <https://www.cosmicpython.com/book/chapter_02_repository.html>
- <https://martinfowler.com/eaaCatalog/repository.html>
- <https://ddd.mikaelvesavuori.se/tactical-ddd/repositories>
