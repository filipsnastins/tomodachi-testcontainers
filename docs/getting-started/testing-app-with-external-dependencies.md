# Testing Applications with External Dependencies

## Running external dependencies locally

Applications don't live in isolation. They depend on other systems - other applications, databases,
file exchanges, cloud provider services, third-party services, etc.
It makes testing difficult - the test environment must have a lot of things configured for the application to work.
Remember spending hours setting up a local development environment?

You should be able to run your application tests on your local machine to get fast feedback about the changes.
Imagine how the workflow would look if the tests worked only in the deployment pipeline -
you had to push changes to version control and wait for the CI server to finish the build every time you wanted to verify a small code change.
It would create unnecessary friction for integrating automated testing into the development workflow.

That's where Testcontainers are very useful - they automate the creation of the application's dependencies.
They're run as Docker containers and thrown away when tests finish.
Testcontainers make configuration of your local development environment easy -
all its components are defined as code in the same repository and created the same way every time you run the tests.

!!! success

    Design your tests so they run locally without any additional configuration.
    Make the tests configure external dependencies automatically, e.g., by starting them as Testcontainers.

## Running production-like versions of external dependencies

Tests should give us confidence that an application will work in a production environment.
The tests are of little value if they're passing, but the application doesn't work for the actual users.
One of the key elements for creating reliable tests is making the development and testing environment as
similar to production as possible. To achieve [dev/prod parity](https://www.12factor.net/dev-prod-parity),
apart from using production-like data and configuration, we must run the same versions of external dependencies in the development environment as in production.
For example, we can run the same versions of databases like PostgreSQL or MongoDB and message brokers like RabbitMQ
(see the [Testing Databases](../guides/testing-databases.md) guide for more examples).
However, it gets more complicated when an application depends on proprietary software or managed cloud services that can't be run locally,
for example, AWS S3 file store or AWS SNS/SQS message broker.

When a particular dependency can't be run locally, e.g., because it's a managed cloud provider service like AWS S3,
we have a couple of testing options:

- Using a real version of an external service, e.g., testing with a real AWS account.
- Mocking the interactions with an external service, e.g., with Python's [`unittest.mock`](https://docs.python.org/3/library/unittest.mock.html#module-unittest.mock).
- Using verified external mocks, e.g., [LocalStack](https://www.localstack.cloud/) and [Moto](https://docs.getmoto.org/en/latest/), for emulating the AWS cloud.

Using a real AWS account for testing is the most production-like way. The tests must use a dedicated AWS account only for autotests and have
safeguards that they're not accidentally connected to a production account. There's a risk of changing production resources if tests are misconfigured.
Using real services will create additional costs in cloud bills and maintenance time that need to be accounted for.
Lastly, the tests will be slower because they'll communicate over the external network and might become flaky if multiple test suites are using the same resources simultaneously.
Ultimately, using the real services shouldn't be your default choice due to the complexity and costs.

The second option is mocking the interactions with external services with mocks, e.g., [`unittest.mock`](https://docs.python.org/3/library/unittest.mock.html#module-unittest.mock).
This way, we verify that the code calls external dependency in a way we expect but doesn't verify if the call would succeed in the real environment.
For example, we can mock calls to the AWS `boto3` client and remove any dependencies on the cloud service in the tests.
The tests will be fast because they remove all network calls. However, they won't ensure that the code will work in the real environment
because we might accidentally misconfigure the mocks, and the tests won't notice that.
Although unit tests are handy because of the low cost and fast runtime, they must be supplemented by other production-like tests.

The last option - verified external mocks - combines the first two approaches.
Since applications usually interact with cloud providers through its REST API,
we can substitute the endpoint URL with a more sophisticated type of mocks that can be run locally.
From the application's perspective, it wouldn't know nor care that it's interacting with a fake service.
What matters is that it behaves the same.

Projects like [LocalStack](https://www.localstack.cloud/) and [Moto](https://docs.getmoto.org/en/latest/) are web applications
that emulate AWS cloud - they provide the same API and behavior for _local development and testing_.
[Similar tools](https://testcontainers.com/modules/?category=cloud) exist for other cloud providers.
Cloud emulators are tested against a real cloud provider to ensure they behave the same; hence, they're verified mocks.
However, they're still not always accurate. You might encounter some corner cases where the mocks didn't catch a problem, and it surfaced only in a real environment.
Check out [LocalStack feature coverage](https://docs.localstack.cloud/user-guide/aws/feature-coverage/)
and [Moto supported services](https://docs.getmoto.org/en/latest/docs/services/index.html) for more details.
Despite that, such services are battle-tested, have extensive open-source community support, and are _good enough_ for most use cases.
Running cloud mocks with Testcontainers is easy because they're simply web applications.
That's the route we'll take in the following sections of this guide.

Lastly, it's worth mentioning that despite testing with verified mocks like LocalStack,
you might stumble upon unsupported features or inaccurate behavior, or you are working with a critical part of the system where the cost of failure is high.
For such cases, you might want to consider testing _parts_ of your application with a real external dependency.
Take all precautions - run such tests only in a deployment pipeline, disable them locally, and always use a separate account dedicated only to automated testing.
To make testing only certain parts of your application easy, modularize those components, for example, with the [Ports & Adapters pattern](../guides/ports-and-adapters/).

!!! success

    To achieve [dev/prod parity](https://www.12factor.net/dev-prod-parity),
    test your application with production-like dependencies with the same configuration.
    You can run the identical versions of some dependencies locally, e.g., PostgreSQL database or RabbitMQ message broker.

    Some dependencies, e.g., a managed cloud provider service, can't be run locally.
    Find an alternative for local development like [LocalStack](https://www.localstack.cloud/) and [Moto](https://docs.getmoto.org/en/latest/)
    AWS cloud emulators.

    If you can't run a dependency locally and no alternatives for local development and testing exist, e.g., Oracle Enterprise Database,
    resort to testing with a dedicated instance running in a separate test environment, or consult your vendor.

## Testing file store application with AWS S3 and LocalStack
