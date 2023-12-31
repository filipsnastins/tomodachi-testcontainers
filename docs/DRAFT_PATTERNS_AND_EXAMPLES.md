# End-to-end and integration testing approaches, patterns and examples

A collection of recipes for testing applications with testcontainers.

- Running tests in parallel/isolation. Do not restart tomodachi container between tests,
  but control isolation with the application means (multitenancy);
  <https://softwaregarden.dev/en/posts/testcontainers/parallel-start-with-prepulling/>
- Using same level of abstractions in the tests
  - Not accessing a database directly
  - Getting the system in the required state via the public API (REST, GraphQL, etc.)
- One test per feature
  - Rather than focusing on testing individual endpoints,
    focus on testing the feature, which may involve multiple endpoints
  - Error handling counts as a feature
- If using Docker multi-stage builds, use the same Dockerfile and release
  target as in production
- Stubbing external HTTP APIs with WireMock
- REST API
- Asynchronous messaging with async probes - sampling
- Mixing REST API and asynchronous messaging tests
- GraphQL
- Scheduled jobs

- [ ] Testing Repositories

- Testcontainers Desktop - <https://testcontainers.com/guides/simple-local-development-with-testcontainers-desktop/>

## Use cases

- [ ] PlantUML-C4 - use icons for technologies

- [x] SQL databases. For testing SQL, we could use SQLite, but ORMs actually don't ensure that the code is portable between different database versions.
      Test the system with a real database that you're using in production.

- Testing integration with SFTP

- AWS mocks like Moto and LocalStack. DynamoDB, S3, SNS SQS etc.

- SQS in, SQS out

- Stubbing collaborator services with WireMock

- Webhooks. WireMock verified

- Testing scheduled jobs. Tomodachi jobs (separate REST endpoint for testing), k8 jobs running as a Python script (with `DockerContainer.exec`)

- Real infra/supporting services like bank-holidays or leader election
  - Internal services - start real versions of them, but not try to test them
  - External services - mock them

## Controlling the system state

- Test isolation

## Performance

- Start containers in parallel
- Pre-pull required docker images in CI
- Start containers only once, isolate the state with application means

- [x] Running tests in parallel with pytest-xdist

## Techniques

- Integration testing - verify that all system components and frameworks are integrated correctly.

- Functional/acceptance testing - verifying system behavior by real world examples.
  - Build a facade on top of your application, invent domain specific language

## Misc

- Debugging. Stop the time by placing a breakpoint and inspect containers
- Attach the debugger
- Export test coverage

## Table of content

```yaml
nav:
  - index.md
  - Recipes:
      - recipes/index.md
      - recipes/testing-databases.md
      - recipes/testing-repositories.md
      - recipes/ports-and-adapters.md
      - recipes/testing-applications.md # How to test your service
      - recipes/parallelizing-tests.md
```
