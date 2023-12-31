# TODOs

## GitHub Actions

...

## Test clients

...

## New testcontainers

- [ ] Explore HTTP mock/stub servers
  - [ ] <https://github.com/mock-server/mockserver>
  - [ ] <https://vcrpy.readthedocs.io/en/latest/>
  - [ ] <https://www.mbtest.org/>
  - [x] <https://wiremock.org/docs/standalone/docker/>

## New test approaches

- Should not be part of the library, but can be used in the example repo

- [ ] Explore [contract testing](https://github.com/pact-foundation/pact-python) between Orders and Customers services
- [ ] Param testing with [Hypothesis](https://hypothesis.readthedocs.io/en/latest/)
- [ ] BDD with [Behave](https://behave.readthedocs.io/en/latest/) or [pytest-bdd](https://pypi.org/project/pytest-bdd/)
- [ ] <https://github.com/hamcrest/PyHamcrest>

## Misc

- [ ] Container lifecycle hooks, e.g. `after_start`, `before_stop`
- [x] Export coverage: install `coverage` from Poetry `test` dependency group
  - Add a new Docker image stage `test` with `coverage` installed
  - [ ] Rewrite code coverage docs section; suggest different ways of starting app in coverage mode

## Docs

- [ ] Rewrite docs about end-to-end tests.
      Testcontainer tests described in this repository are not integrated end-to-end tests,
      but rather isolated, individual microservice integration test.
- [ ] Use cases, patterns and good practices (examples with C4 diagrams)

## Testing

- [x] Run tests in parallel with `pytest-xdist`
  - [x] Test in GitHub Actions
  - [ ] Document in README and recipes
- [ ] Docker-from-Docker test
