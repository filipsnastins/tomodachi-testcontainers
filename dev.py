# noqa: INP001
import os
from subprocess import check_call


def hooks() -> None:
    check_call(["poetry", "run", "pre-commit", "run", "--all-files"])


def format() -> None:
    check_call(
        [
            "poetry",
            "run",
            "autoflake",
            "--in-place",
            "--recursive",
            "--remove-all-unused-imports",
            "--remove-unused-variables",
            "--ignore-init-module-imports",
            ".",
        ]
    )
    check_call(["poetry", "run", "ruff", "check", "--fix", "."])
    check_call(["poetry", "run", "black", "."])
    check_call(["poetry", "run", "isort", "."])


def lint() -> None:
    check_call(["poetry", "run", "ruff", "check", "."])
    check_call(["poetry", "run", "flake8", "."])
    check_call(["poetry", "run", "pylint", "src/tomodachi_testcontainers", "tests"])
    check_call(["poetry", "run", "mypy", "src", "tests"])
    check_call(["poetry", "run", "mypy", "--config", "examples/pyproject.toml", "examples"])
    check_call(["poetry", "run", "mypy", "--config", "docs_src/pyproject.toml", "docs_src"])
    check_call(["poetry", "run", "bandit", "-r", "src", "examples"])


def test() -> None:
    check_call(["poetry", "run", "pytest", "-v"])


def test_docs_src() -> None:
    check_call(["poetry", "run", "pytest", "-v", "docs_src"])


def test_ci() -> None:
    check_call(["poetry", "run", "coverage", "erase"])
    check_call(
        [
            "poetry",
            "run",
            "pytest",
            "--cov",
            "--cov-append",
            "--cov-branch",
            "--cov-report=xml:build/coverage.xml",
            "--cov-report=html:build/htmlcov",
            "-v",
            "--junitxml=build/tests.xml",
            "-n",
            "auto",
        ],
        env={"TOMODACHI_TESTCONTAINER_EXPORT_COVERAGE": "1", **os.environ},
    )
