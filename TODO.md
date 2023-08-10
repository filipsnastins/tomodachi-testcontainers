# TODOs

## GitHubActions

...

## Test clients

...

## New testcontainers

- [ ] Rename `tomodachi_image` to something generic like `service_image`;
      this library seem to work just fine with any other framework,
      which hasn't been thought thoroughly before creating this library.

- [ ] HTTP test server
  - <https://github.com/mock-server/mockserver>
  - <https://vcrpy.readthedocs.io/en/latest/>
  - <https://github.com/stripe/stripe-mock>
  - <https://stripe.com/docs/automated-testing>
  - <https://wiremock.org/docs/standalone/docker/>

## New test approaches

- Should not be part of the library, but can be used in the example repo

- [ ] Explore [contract testing](https://github.com/pact-foundation/pact-python) between Orders and Customers services
- [ ] Param testing with [Hypothesis](https://hypothesis.readthedocs.io/en/latest/)
- [ ] BDD with [Behave](https://behave.readthedocs.io/en/latest/) or [pytest-bdd](https://pypi.org/project/pytest-bdd/)
- [ ] <https://github.com/hamcrest/PyHamcrest>

## Misc

...

## Docs

...

## Testing

- [ ] Docker-from-Docker test
