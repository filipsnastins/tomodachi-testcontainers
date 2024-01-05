# Tomodachi Testcontainers

![Build Status](https://github.com/filipsnastins/tomodachi-testcontainers/actions/workflows/main.yml/badge.svg)
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Ffilipsnastins%2Ftomodachi-testcontainers.svg?type=shield&issueType=license)](https://app.fossa.com/projects/git%2Bgithub.com%2Ffilipsnastins%2Ftomodachi-testcontainers?ref=badge_shield&issueType=license)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=filipsnastins_tomodachi-testcontainers&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=filipsnastins_tomodachi-testcontainers)
[![CodeScene Code Health](https://codescene.io/projects/46808/status-badges/code-health)](https://codescene.io/projects/46808)
[![CodeScene System Mastery](https://codescene.io/projects/46808/status-badges/system-mastery)](https://codescene.io/projects/46808)
[![codecov](https://codecov.io/gh/filipsnastins/tomodachi-testcontainers/graph/badge.svg?token=ZPWNYCRTV0)](https://codecov.io/gh/filipsnastins/tomodachi-testcontainers)
[![Maintainability](https://api.codeclimate.com/v1/badges/d3002235e028a3f713c9/maintainability)](https://codeclimate.com/github/filipsnastins/tomodachi-testcontainers/maintainability)

Tomodachi Testcontainers is a Python library built on top of [testcontainers-python](https://github.com/testcontainers/testcontainers-python).
It provides [Testcontainers](https://github.com/filipsnastins/tomodachi-testcontainers/tree/main/src/tomodachi_testcontainers/containers),
[pytest fixtures](https://github.com/filipsnastins/tomodachi-testcontainers/tree/main/src/tomodachi_testcontainers/pytest),
and [test clients](https://github.com/filipsnastins/tomodachi-testcontainers/tree/main/src/tomodachi_testcontainers/clients)
for convenient use of Testcontainers with [pytest](https://docs.pytest.org/)
and testing applications built with the [Python Tomodachi framework](https://github.com/kalaspuff/tomodachi).

> [Testcontainers](https://testcontainers.com/) is an open-source framework for providing throwaway,
> lightweight instances of databases, message brokers, web browsers, or just about anything that can run in a Docker container.
> It facilitates the use of Docker containers for functional, integration, and end-to-end testing.
> — <https://testcontainers.com/>

This library was created to explore and learn Testcontainers. Although initially intended to be used with the Tomodachi framework,
it works for testing applications built with any other Python framework like Flask, FastAPI, etc.

## Documentation

Find documentation at <https://filipsnastins.github.io/tomodachi-testcontainers/>

The official Testcontainers documentation is at <https://testcontainers.com/>

## Installation

Install with [pip](https://pip.pypa.io/en/stable/getting-started/):

```sh
pip install tomodachi-testcontainers
```

Install with [Poetry](https://python-poetry.org/):

```sh
poetry add --group dev tomodachi-testcontainers
```

Find a list of extras in the complete [installation reference](https://filipsnastins.github.io/filipsnastins/tomodachi-testcontainers/installation/).

## A Simple Example

The `Hello, world` Tomodachi service:

```py
# src/hello.py
import tomodachi
from aiohttp import web


class Service(tomodachi.Service):
    @tomodachi.http("GET", r"/hello/?")
    async def hello(self, request: web.Request) -> web.Response:
        name = request.query.get("name", "World")
        return web.json_response(data={"message": f"Hello, {name}!"})
```

`testcontainers_docker_image` fixture builds a Docker image with a Dockerfile from the current working directory.
`tomodachi_container` fixture starts a new Docker container running the `hello` service on an available port.
`test_hello_testcontainers` sends a `GET /hello?name=Testcontainers` request to the running container.

```py
# tests/test_hello.py
from typing import Generator, cast

import httpx
import pytest

from tomodachi_testcontainers import TomodachiContainer
from tomodachi_testcontainers.utils import get_available_port


@pytest.fixture(scope="session")
def tomodachi_container(testcontainers_docker_image: str) -> Generator[TomodachiContainer, None, None]:
    with TomodachiContainer(
        image=testcontainers_docker_image,
        edge_port=get_available_port(),
    ).with_command("tomodachi run src/hello.py --production") as container:
        yield cast(TomodachiContainer, container)


@pytest.mark.asyncio()
async def test_hello_testcontainers(tomodachi_container: TomodachiContainer) -> None:
    async with httpx.AsyncClient(base_url=tomodachi_container.get_external_url()) as client:
        response = await client.get("/hello", params={"name": "Testcontainers"})

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Testcontainers!"}
```

## Links

- Documentation: <https://filipsnastins.github.io/tomodachi-testcontainers/>
- Releases and Changelog: <https://github.com/filipsnastins/tomodachi-testcontainers/releases>
- PyPI: <https://pypi.org/project/tomodachi-testcontainers/>
- Source Code: <https://github.com/filipsnastins/tomodachi-testcontainers>
- Reference - Code API: <https://filipsnastins.github.io/tomodachi-testcontainers/reference/>
