# Testing Databases

...

## Using in-memory SQLite relational database in tests

### Use case

If an application uses relational database and Object-Relational Mapper (ORM) for implementing a data layer,
it's easy to replace a production database, e.g. PostgreSQL or MySQL, with an in-memory SQLite database.
SQLite does not require any additional setup or dependencies, and it might seem as a convenient choice in automated testing.

For example, using SQLAlchemy, set the database URL to `sqlite://` to connect to a in-memory SQLite database;
it will use built-in Python module `sqlite3`:

```py
from sqlalchemy import create_engine

engine = create_engine("sqlite://")
```

### Drawbacks

Using SQLite in tests creates a compatibility problem between the SQLite and your production database,
because the two database technologies support different features and implement some SQL statements differently.

ORMs try to abstract away these differences, especially different SQL flavours, but not eliminate them completely.
It's a misconception that ORMs are designed to enable switch from one relational database technology to another without changes to the application code.

If SQLite is used for testing, the application code must only use common features that are available in both the SQLite and the production database of choice.
This cuts the benefits an application can get by using unique features of a particular database technology,
potentially lowering performance and increasing complexity of the application code.

In addition, it's not guaranteed that the application that passed the tests using SQLite will work in a real environment with the production database,
because the ORM can still fail to work with the production database due to undiscovered differences in behavior.

## Using production-like database in tests

Wether you're using a relational or NoSQL database, it's a good idea to use the same database in tests as in production.
Testconainters make it easy to setup a database for testing and delete it when the tests are finished.

- [ ] Use real database in Testcontainers. Configure it in the same way as in production.

### Improving test performance

- Disable `fsync` - link to `pythonspeed` blog.

## Testing Repositories

- [ ] Test Repository in isolation with a real database.
- [ ] Use fakes/mocks in other unit tests where database access is not required.
- [ ] Test your fake Repository with the same suite of tests as the real Repository.
- [ ] Where it makes sense to use Repository pattern, and where is it an overkill?
- [ ] Round-trip testing to not expose Repository implementation details.

![Container Diagram - Application with Relational Database](../architecture/c4/level_2_container/01_app_with_relational_db.png)

![Component Diagram - Application with Relational Database](../architecture/c4/level_3_component/01_app_with_relational_db.png)

## References

- <https://pythonspeed.com/articles/faster-db-tests/>
- <http://michael.robellard.com/2015/07/dont-test-with-sqllite-when-you-use.html>
- <https://martinfowler.com/eaaCatalog/repository.html>
- <https://www.cosmicpython.com/book/chapter_02_repository.html>
