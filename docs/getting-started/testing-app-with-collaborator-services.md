# Testing Applications with Collaborator Services

WireMock

We want to test our application in an environment as close to the real world as possible.
We can deploy the app to a staging environment and test it there, but it limits what kind of tests we can do.
Testing most error-handling scenarios is impossible because we can't force another system to misbehave unless it has known and reproducible bugs.
For example, we'd like to test what happens when an external system is down or responds with unexpected data,
but we don't have control over the real instance of the external system.
Testing happy-path scenarios might also be difficult
