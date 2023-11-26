# noqa: INP001
import os
from subprocess import check_call


def hooks() -> None:
    check_call(["pre-commit", "run", "--all-files"])


def format() -> None:
    check_call(["ruff", "check", "--fix", "."])
    check_call(["black", "."])
    check_call(["isort", "."])
    check_call(
        [
            "autoflake",
            "--in-place",
            "--recursive",
            "--remove-all-unused-imports",
            "--remove-unused-variables",
            "--ignore-init-module-imports",
            ".",
        ]
    )


def lint() -> None:
    check_call(["ruff", "check", "."])
    check_call(["flake8", "."])
    check_call(["pylint", "src/tomodachi_testcontainers", "tests"])
    check_call(["mypy", "src", "tests", "examples"])
    check_call(["bandit", "-r", "src", "examples"])


def test() -> None:
    check_call(["pytest", "-v"])


def test_ci() -> None:
    check_call(["coverage", "erase"])
    check_call(
        [
            "pytest",
            "--cov",
            "--cov-append",
            "--cov-branch",
            "--cov-report=xml:build/coverage.xml",
            "--cov-report=html:build/htmlcov",
            "-v",
            "--junitxml=build/tests.xml",
        ],
        env={"TOMODACHI_TESTCONTAINER_EXPORT_COVERAGE": "1", **os.environ},
    )
