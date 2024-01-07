# Included Testcontainers

Below is the list of Testcontainers included in this library.
Feel free to explore how they're implemented and create your own Testcontainers as needed -
see [Creating new Testcontainers](./guides/creating-new-testcontainers.md)

| Container Name | Default Image                     | Fixture                |
| :------------- | :-------------------------------- | :--------------------- |
| Tomodachi      | n/a                               | n/a                    |
| Moto           | `motoserver/moto:latest`          | `moto_container`       |
| LocalStack     | `localstack/localstack:3`         | `localstack_container` |
| Minio          | `minio/minio:latest`              | `minio_container`      |
| DynamoDBAdmin  | `aaronshaf/dynamodb-admin:latest` | n/a                    |
| SFTP           | `atmoz/sftp:latest`               | `sftp_container`       |
| WireMock       | `wiremock/wiremock:latest`        | `wiremock_container`   |
| MySQL          | `mysql:8`                         | `mysql_container`      |
| PostgreSQL     | `postgres:16`                     | `postgres_container`   |

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
