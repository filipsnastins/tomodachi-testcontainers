# Applying End-to-End Tests With Testcontainers

After going through the guides and examples, you might ask, where do end-to-end tests with Testcontainers fit into the whole application's testing strategy?
There's no universal answer, so this section will do its best to outline some pointers toward better and more reliable application testing.

## Building confidence in automated tests

Automated tests must give us confidence that the system is in a releasable state -
it does what the system users want (user-focused tests) and does that right (developer-focused tests).
The tests are of little value if they're passing, but the application doesn't work for the actual users.
Therefore, the system must be tested in a production-like environment close to real-world usage.
The specific test tools and frameworks matter less than building confidence that the automated test suite is robust and trustworthy.

Testcontainers are a tool for creating an isolated, controlled, and production-like test environment
without the disadvantages of depending on complex and shared staging environments.
With Testcontainers, we can test an application in a production-like environment, building confidence that the application will work for real users.

Since such end-to-end tests tend to be lengthy to write and sometimes tricky to set up,
e.g., when an application has a lot of external dependencies, you need to make a conscious choice about how many such tests you want to have.
There's no correct answer here, so let's look at different approaches and their benefits and disadvantages.

## Using end-to-end tests to ensure correct integration of the system's components

One of the Testcontainer end-to-end test applications is ensuring that all system's components are configured and working together correctly.
It's useful to test because applications depend on many other libraries and tools.
Although the external components are tested individually by their developers, we still must ensure that our application uses them correctly.

To ensure that all system components are configured correctly, we'll write a limited amount of end-to-end tests and touch all system integration points.
The book [Architecture Patterns with Python](https://www.cosmicpython.com/) (Harry Percival and Bob Gregory)
describes a useful [rule of thumb for the use of different types of tests](https://www.cosmicpython.com/book/chapter_05_high_gear_low_gear.html#types_of_test_rules_of_thumb):

- **Aim for one end-to-end test per feature; error handling counts as a feature** - it suggests using end-to-end tests to demonstrate that the feature works
  and all the system components that build the feature are working together correctly.
  It means that end-to-end tests shouldn't be used as the main way of testing the system due to their cost and brittleness
  but rather as a way to supplement other tests - service layer tests and unit tests.

- **Write the bulk of your tests against the service layer; maintain a small core of tests written against your domain model** -
  if you keep your application's business logic decoupled from the framework, e.g., Django,
  you can test most of the system without the need to rely on slow, real dependencies.
  You can use fakes and mocks to simulate input/output (databases, message brokers, external systems) and focus tests on the core business logic.

It is important to note that end-to-end tests should focus on testing the application's public API rather than internal implementation details,
for example, what data was saved to the PostgreSQL database table. A single end-to-end test might call multiple API endpoints,
exercising the whole system and simulating a realistic user's journey. Focus on testing user behaviors rather than individual application endpoints.

!!! note

    The [Architecture Patterns with Python](https://www.cosmicpython.com/) book neatly describes patterns for building robust and testable applications.
    I highly recommend this as an introduction to building clean and maintainable systems. Also, the book is free! 📖

## Using end-to-end tests as a base for the system's test strategy

[Test Pyramid](https://martinfowler.com/bliki/TestPyramid.html) is a famous application testing strategy - most tests are isolated unit tests,
fewer tests are integration/service tests, and the least amount of tests are end-to-end/UI tests.
This approach is often used in testing monolithic applications.

When using more service-oriented architectures like microservices, individual applications are smaller,
so the forces behind the Test Pyramid change - there's less need to segregate tests in unit/integration/end-to-end because the amount of tests is also smaller.
Testing Honeycomb proposed at Spotify is a different mental model for thinking about testing microservices.
Read the full article - [Testing of Microservices at Spotify Engineering Blog](https://engineering.atspotify.com/2018/01/testing-of-microservices/).

It's important to remember not to get caught up in the debates between different testing shapes and the correct number of test types.
Focus on the value of the tests - that the system does what users want (user-focused tests) and does it right (developer-focused tests).
Read up [On the Diverse And Fantastical Shapes of Testing](https://martinfowler.com/articles/2021-test-shapes.html) on Martin Fowler's site.

## Next Steps

I hope that this introduction to Testcontainers and end-to-end tests was useful.
It wasn't meant to be an exhaustive guide to automated testing,
so I'll leave some valuable and free resources about application testing for further reading:

- [Testing for Software Engineers](https://testing.mikaelvesavuori.se/) by Mikael Vesavuori.
- [Architecture Patterns with Python](https://www.cosmicpython.com/) Harry Percival and Bob Gregory.
- [Test-Driven Development with Python](https://www.obeythetestinggoat.com/) by Harry Percival.

If you want to continue exploring Testcontainers, check out the [Guides](../guides/) section
and the official [Testcontainers site](https://testcontainers.com/). 👋
