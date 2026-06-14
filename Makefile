.PHONY: setup
setup:
	uv sync --all-extras --dev
	uv run pre-commit install

.PHONY: hooks
hooks:
	uv run pre-commit run --all-files

.PHONY: format
format:
	uv run autoflake --in-place --recursive --remove-all-unused-imports --remove-unused-variables --ignore-init-module-imports .
	uv run ruff check --fix .
	uv run black .
	uv run isort .

.PHONY: lint
lint:
	uv run flake8 .
	uv run ruff check .
	uv run pylint src/tomodachi_testcontainers tests
	uv run mypy src tests
	uv run mypy --config examples/pyproject.toml examples
	uv run mypy --config docs_src/pyproject.toml docs_src
	uv run bandit -r src examples
	uv run pydocstringformatter --style=pep257 --style=numpydoc .

.PHONY: test
test:
	uv run pytest -v

.PHONY: test-docs-src
test-docs-src:
	uv run pytest -v docs_src

.PHONY: test-ci
test-ci:
	env TOMODACHI_TESTCONTAINER_EXPORT_COVERAGE=1 \
	uv run pytest \
		--cov \
		--cov-append \
		--cov-branch \
		--cov-report=xml:build/coverage.xml \
		--cov-report=html:build/htmlcov \
		-v \
		--junitxml=build/tests.xml \
		-n auto \
		--force-flaky \
		--max-runs=3 \
		--no-success-flaky-report
