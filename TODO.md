# TODOs

## GitHub Actions

...

## Test clients

- [ ] Remove cache from SNSSQSTestClient; make `moto_snssqs_tc` and `localstack_snssqs_tc` fixtures session scoped.
- [ ] Make message envelope optional in SNSSQSTestClient.

## New Testcontainers

- [ ] Explore HTTP mock/stub servers
  - [ ] <https://github.com/mock-server/mockserver>
  - [ ] <https://vcrpy.readthedocs.io/en/latest/>
  - [ ] <https://www.mbtest.org/>
  - [x] <https://wiremock.org/docs/standalone/docker/>

## New test approaches

- Should not be part of the library but can be used in an example repo:

- [ ] Explore [contract testing](https://github.com/pact-foundation/pact-python) between Orders and Customer services
- [ ] Param testing with [Hypothesis](https://hypothesis.readthedocs.io/en/latest/)
- [ ] BDD with [Behave](https://behave.readthedocs.io/en/latest/) or [pytest-bdd](https://pypi.org/project/pytest-bdd/)
- [ ] <https://github.com/hamcrest/PyHamcrest>

## Pytest fixtures

- [ ] Add `wiremock_container` fixture

## Misc

- [ ] Container lifecycle hooks, e.g., `after_start`, `before_stop`
- [x] Export coverage: install `coverage` from Poetry `test` dependency group.
  - [ ] Add a new Docker image stage `test` with `coverage` installed.
  - [ ] Rewrite the code coverage docs section; suggest different ways of starting the app in coverage mode.
- [ ] Change environment variable prefix from `TOMODACHI_TESTCONTAINER_` to `TESTCONTAINER_`.

## Docs

- [ ] Rewrite docs about end-to-end tests.
  - Testcontainer tests described in this repository are not integrated end-to-end tests,
    but rather isolated, individual application's integration test.
  - <https://bsideup.github.io/posts/spring_boot_in_container> - the term E2E is used here.
- [ ] Use cases, patterns, and good practices (examples with C4 diagrams).
- [ ] Rename `recipes` into `guides`.
- [ ] Move "how to run in CI" guide from <https://github.com/filipsnastins/tomodachi-testcontainers-github-actions>.
- [ ] Add Docker image override environment variables to "Included Testcontainers" page.

## Testing

- [ ] Docker-from-Docker test.
