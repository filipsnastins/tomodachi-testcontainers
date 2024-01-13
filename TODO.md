# TODOs

## GitHub Actions

...

## Test clients

...

## New Testcontainers

...

## New test approaches

- [ ] Param testing with [Hypothesis](https://hypothesis.readthedocs.io/en/latest/)

## Pytest fixtures

...

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
- [x] Rename `recipes` into `guides`.
- [ ] Move "how to run in CI" guide from <https://github.com/filipsnastins/tomodachi-testcontainers-github-actions>.
- [ ] Add Docker image override environment variables to "Included Testcontainers" page.
- [x] In the guides, mention overriding `event_loop` fixture to session scope.

## Testing

- [ ] Docker-from-Docker test.
