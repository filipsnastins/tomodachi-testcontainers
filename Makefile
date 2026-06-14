.PHONY: setup
setup:
	uv sync --all-extras --dev
	uv run pre-commit install

.PHONY: hooks
hooks:
	uv run pre-commit run --all-files

.PHONY: format
format:
	uv run ruff format .
	uv run ruff check --fix .

.PHONY: lint
lint:
	uv run ruff format --check .
	uv run ruff check .
	uv run mypy src tests
	uv run mypy --config examples/pyproject.toml examples
	uv run mypy --config docs_src/pyproject.toml docs_src

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
