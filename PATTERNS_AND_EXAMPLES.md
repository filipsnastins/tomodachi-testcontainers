# End-to-end and integration testing approaches, patterns and examples

A collection of recipes for testing applications with testcontainers.

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
- Asynchronous messaging with async probes
- Mixing REST API and asynchronous messaging tests
- GraphQL
- Scheduled jobs
