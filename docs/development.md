# Development

- Install dev dependencies with [Poetry](https://python-poetry.org/).

```sh
poetry install --all-extras --with dev,docs
poetry shell
pre-commit install
```

- Run tests.

```sh
docker network create tomodachi-testcontainers

poetry run test  # Run tests during development
poetry run test-docs-src  # Test documentation code examples
poetry run test-ci  # Run all tests with code coverage
```

- Format and lint code.

```sh
poetry run format
poetry run lint
```

- Run all commit hooks at once.

```sh
poetry run hooks
```

- Build package release.

```sh
poetry build
```

- Develop documentation with [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).

```sh
mkdocs serve
```

- Generate C4 diagrams with PlantUML (get plantuml.jar at <https://plantuml.com/starting>).

```sh
export JAVA_HOME=`/usr/libexec/java_home -v 21`

java -jar plantuml.jar -DRELATIVE_INCLUDE="." docs/**/*.puml
```

- Run PlantUML server.

```sh
docker run -d -p 8080:8080 plantuml/plantuml-server:jetty
```
