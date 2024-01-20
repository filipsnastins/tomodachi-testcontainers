# Managing Test Isolation

Test isolation is about ensuring that one test's result doesn't impact another test's result.
We want our tests to be deterministic and not dependent on other tests.
If tests are not isolated, they become flaky - they sometimes fail because the system's state was modified elsewhere.
Flaky tests erode the trust in the test suite - we stop trusting our automated tests and soon abandon them altogether.
Therefore, we should ensure that our tests are robust and isolated.

There are many techniques for test isolation. For example, the Django framework's test client provides
a [`TransactionTestCase`](https://docs.djangoproject.com/en/5.0/topics/testing/tools/#django.test.TransactionTestCase)
helper that rollbacks database transactions after every test, ensuring that the database is always in a known state.
This approach works for lower-level tests with direct access to the framework code, but doesn't work for Testcontainer test.
We don't have access to internal working details for a particular framework on the end-to-end test level.
We're testing an application's public API, disregarding any implementation details of frameworks and other libraries that power our applications.

When writing end-to-end tests with Testcontainers, we should use other test isolation approaches,
which often are simpler than rollbacking transactions or resetting databases after every test.
Here's a list of the most common options, ordered from fastest to slowest in terms of test performance:

- Managing test isolation with the application's means (recommended!).
- Recreating specific resources after every test, for example, a database table or S3 bucket.
- Recreating some Testcontainers after every test.
- Recreating all Testcontainers after every test (not recommended!).

## Managing test isolation with the application's means

It's a good practice to start Testcontainers only once per test session;
it takes time for containers to start, so recreating them after every test significantly impacts test performance.
However, working with the same containers creates challenges with managing test isolation because each test will leave new or changed data behind.

Luckily, your application under test already has some way of managing isolation - TODO

## Draft

There are multiple approaches for managing test isolation:

- Restart containers after every test so that applications always start from a known clean state - the easiest but the slowest approach.
  Remove `scope="session"` from Testcontainer's `@pytest.fixture` definition.

- Truncating/recreating datastores after every test - faster than restarting the entire container.
  For example, we could recreate an S3 bucket or database table after every test.

- Managing test isolation with the application means - the fastest approach, but it might not be feasible in all use cases.
  Most applications have a way of managing their data isolation, e.g., applications that scope what data a logged-in user can see.
