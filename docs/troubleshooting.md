# Troubleshooting

Error on running tests with pytest: `ScopeMismatch: You tried to access the function scoped fixture event_loop with a session scoped request object, involved factories.`

: **Problem:** the error occurs when you're using asynchronous fixtures with a scope higher than `function`,
e.g., fixture `moto_container` has `session` scope.
The default `event_loop` fixture provided by `pytest-asyncio` is a function-scoped fixture, so it can't be used with session-scoped fixtures.

: **Solution:** override the `event_loop` fixture with a session-scoped fixture by placing it in your project's default `conftest.py`.
See [tests/conftest.py](https://github.com/filipsnastins/tomodachi-testcontainers/blob/main/tests/conftest.py) for an example:
