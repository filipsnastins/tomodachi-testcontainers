# Old Readme

## Benefits and dangers of end-to-end tests

### Building confidence of releasability

The examples from this guide and [tests/test_services](tests/test_services) show that end-to-end tests
are powerful kind of tests. End-to-end test are used to test the system from its users perspective,
be it a human being or another application. End-to-end tests test the system from the outside,
on its public API level.

_End-to-end tests build the last bit of confidence of releasability -
that the system will work in production without more manual testing._

_To get a high confidence of releasability, it's necessary to test the system with real dependencies and infrastructure.
Testcontainers make it easy to spin up real dependencies in Docker containers, and throw them away
when the tests are finished. They work in the same way locally and in the deployment pipeline, so you need to
setup test suite only once._

### ⚠️ Mind the Test Pyramid - don't overdo end-to-end tests

Despite many benefits of end-to-end tests, they are the most expensive kind 💸 -
they're slow, sometimes [flaky](https://martinfowler.com/articles/nonDeterminism.html),
it's hard to understand what's broken when they fail.

End-to-end tests are expensive, but necessary to build confidence of releasability,
so it's important to use them intentionally and know about other kinds of tests.
After all, we can't be confident that the system _really_ works in production if we haven't
tested it in the environment as close to production as possible.

The [Test Pyramid](https://martinfowler.com/bliki/TestPyramid.html) is a useful thinking model about
different kinds of tests and their value. It proposes that the majority of tests should be unit tests,
followed by integration tests, and the least amount of tests should be end-to-end tests.

The book [Architecture Patterns with Python](https://www.cosmicpython.com/) by Harry Percival and Bob Gregory
describes a useful [rule of thumb for use of different types of tests](https://www.cosmicpython.com/book/chapter_05_high_gear_low_gear.html#types_of_test_rules_of_thumb):

- **Aim for one end-to-end test per feature; error handling counts as a feature** - it suggests using
  end-to-end tests to demonstrate that the feature works, and all the system components that build
  the feature are working together correctly. _It means that end-to-end tests shouldn't be used
  as the main way of testing the system due to their cost and brittleness,
  but rather as a way to supplement service layer and unit tests._

- **Write the bulk of your tests against the service layer; maintain a small core of tests written against your domain model** -
  if you keep your application business logic use cases decoupled from the framework,
  you can test most of the system without the need to rely on slow, real dependencies.
  You can use fakes for simulating input/output (databases, message brokers, external system adapters),
  making the tests focused on the business logic.

The [Architecture Patterns with Python](https://www.cosmicpython.com/) book neatly describes patterns for building
robust and testable applications, so if you want to learn more, I highly recommend it as a starting point.
Also, it's free! 📖

Another point worth noting about different test types is that, ideally, tests should be written on the same level of abstraction. ⚖️

If means that if you're writing, for example, end-to-end tests, you should strive to use only the public API of the application -
HTTP endpoints, message topics or queues, etc. - to test the system, and not use any internal implementation details, like
directly accessing a database.

For example, the test `test_create_order` in [tests/test_services/test_order_service.py](tests/test_services/test_order_service.py)
asserts that an order has been created by calling the public API endpoints `GET /orders/<order_id>`,
instead of querying `orders` table directly to assert that the order row has been created with correct data.

This way, the internal `orders` table can be changed without breaking end-to-end tests,
as long as the public API stays the same. However, if the `GET /orders` has a bug,
all the tests that use `GET /orders` will fail, and it might not be intuitive to find the problem right away.
That's a trade-off we need to make in order to not expose system's private data structures and internal implementation details.

The same principle applies to other test types. In service layer tests, you'd be using only
use case functions to test the system, and not accessing domain model objects directly.
In case of domain model tests or unit tests, you'd be testing only public methods of the objects,
and not private methods and attributes.
Since there're no explicit private methods and attributes in Python, it's important to remember this,
and use automated code quality assertion tools like `flake8` and `pylint` as a safety net.
