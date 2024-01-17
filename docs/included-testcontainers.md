# Included Testcontainers

Below is the list of Testcontainers included in this library.
Feel free to explore how they're implemented and create your Testcontainers when needed -
see [Creating new Testcontainers](./guides/creating-new-testcontainers.md)

| Container Name                                                              | Default Image                     | Fixture                                                                          |
| :-------------------------------------------------------------------------- | :-------------------------------- | :------------------------------------------------------------------------------- |
| [`TomodachiContainer`][tomodachi_testcontainers.TomodachiContainer]         | n/a                               | n/a                                                                              |
| [`MotoContainer`][tomodachi_testcontainers.MotoContainer]                   | `motoserver/moto:latest`          | [`moto_container`][tomodachi_testcontainers.fixtures.moto_container]             |
| [`LocalStackContainer`][tomodachi_testcontainers.LocalStackContainer]       | `localstack/localstack:3`         | [`localstack_container`][tomodachi_testcontainers.fixtures.localstack_container] |
| [`MinioContainer`][tomodachi_testcontainers.MinioContainer]                 | `minio/minio:latest`              | [`minio_container`][tomodachi_testcontainers.fixtures.minio_container]           |
| [`DynamoDBAdminContainer`][tomodachi_testcontainers.DynamoDBAdminContainer] | `aaronshaf/dynamodb-admin:latest` | n/a                                                                              |
| [`SFTPContainer`][tomodachi_testcontainers.SFTPContainer]                   | `atmoz/sftp:latest`               | [`sftp_container`][tomodachi_testcontainers.fixtures.sftp_container]             |
| [`WireMockContainer`][tomodachi_testcontainers.WireMockContainer]           | `wiremock/wiremock:latest`        | [`wiremock_container`][tomodachi_testcontainers.fixtures.wiremock_container]     |
| [`MySQLContainer`][tomodachi_testcontainers.MySQLContainer]                 | `mysql:8`                         | [`mysql_container`][tomodachi_testcontainers.fixtures.mysql_container]           |
| [`PostgreSQLContainer`][tomodachi_testcontainers.PostgreSQLContainer]       | `postgres:16`                     | [`postgres_container`][tomodachi_testcontainers.fixtures.postgres_container]     |

!!! note

    See [configuration options](./configuration-options.md) for containers configuration settings.

## Tomodachi

Tomodachi - a lightweight microservices library on Python asyncio.

Repository: <https://github.com/kalaspuff/tomodachi>

## Moto

Moto is a library that allows your tests to mock out AWS Services.

Repository: <https://github.com/getmoto/moto>

Docker Hub: <https://hub.docker.com/r/motoserver/moto>

## LocalStack

LocalStack provides an easy-to-use test/mocking framework for developing cloud applications.

Repository: <https://github.com/localstack/localstack>

DockerHub: <https://hub.docker.com/r/localstack/localstack>

## Minio

MinIO is a High Performance Object Storage released under GNU Affero General Public License v3.0. It is API compatible with Amazon S3 cloud storage service.

Repository: <https://github.com/minio/minio>

DockerHub: <https://hub.docker.com/r/minio/minio>

## DynamoDB Admin

GUI for DynamoDB Local, dynalite, localstack etc. Useful for exploring DynamoDB tables and data during development and testing.

Repository: <https://github.com/aaronshaf/dynamodb-admin>

DockerHub: <https://hub.docker.com/r/aaronshaf/dynamodb-admin>

## SFTP

Easy to use SFTP (SSH File Transfer Protocol) server with OpenSSH.

Repository: <https://github.com/atmoz/sftp>

DockerHub: <https://hub.docker.com/r/atmoz/sftp>

- Available as an extra dependency `sftp` - `pip install tomodachi-testcontainers[sftp]`.

## WireMock

WireMock is a tool for building mock APIs. Create stable development environments,
isolate yourself from flaky 3rd parties and simulate APIs that don't exist yet.

Repository: <https://github.com/wiremock/wiremock>

DockerHub: <https://hub.docker.com/r/wiremock/wiremock>

Python SDK: <https://github.com/wiremock/python-wiremock>

- WireMock Python SDK can be installed as an extra dependency `wiremock` - `pip install tomodachi-testcontainers[wiremock]`.

## MySQL

MySQL is a widely used, open-source relational database management system (RDBMS).

DockerHub: <https://hub.docker.com/_/mysql>

- Available as an extra dependency `mysql` - `pip install tomodachi-testcontainers[mysql]`.

## PostgreSQL

The PostgreSQL object-relational database system provides reliability and data integrity.

DockerHub: <https://hub.docker.com/_/postgres>

- Available as an extra dependency `postgres` - `pip install tomodachi-testcontainers[postgres]`.
