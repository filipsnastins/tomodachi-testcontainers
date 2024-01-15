# Testing Applications Built with other Frameworks like Flask, FastAPI, or Django

With Testcontainers, you can test any app running in a container.

Using the [`testcontainer_image`][tomodachi_testcontainers.pytest.testcontainer_image] pytest fixture,
you can build a Docker image with Dockerfile from a current working directory.
Then, you can use the built Docker image ID to start a new container.
To learn how to create your new Testcontainers, see the previous guide - [Creating new Testcontainers](./creating-new-testcontainers.md).

Below are examples of running Flask, FastAPI, and Django applications with Testcontainers.
The specific framework doesn't matter as long as it runs in a container.

## Flask example

```py title="src/flask_app.py"
--8<-- "docs_src/creating_testcontainers/flask_app.py"
```

```py title="tests/test_flask_app.py"
--8<-- "docs_src/creating_testcontainers/test_flask_app.py"
```

## FastAPI example

```py title="src/fastapi_app.py"
--8<-- "docs_src/creating_testcontainers/fastapi_app.py"
```

```py title="tests/test_fastapi_app.py"
--8<-- "docs_src/creating_testcontainers/test_fastapi_app.py"
```

## Django example

```py title="src/django_app/django_app/views.py"
--8<-- "docs_src/creating_testcontainers/django_app/django_app/views.py"
```

```py title="tests/test_django_app.py"
--8<-- "docs_src/creating_testcontainers/test_django_app.py"
```
