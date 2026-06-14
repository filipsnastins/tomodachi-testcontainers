# Development

- Install dev dependencies with [uv](https://docs.astral.sh/uv/).

```sh
uv sync --all-extras
uv run pre-commit install
```

- Run tests.

```sh
docker network create tomodachi-testcontainers

make test  # Run tests during development
make test-docs-src  # Test documentation code examples
make test-ci  # Run all tests with code coverage
```

- Format and lint code.

```sh
make format
make lint
```

- Run all commit hooks at once.

```sh
make hooks
```

- Build package release.

```sh
uv build
```

- Develop documentation with [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).

```sh
uv run mkdocs serve
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
