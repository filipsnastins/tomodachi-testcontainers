.PHONY: hooks
hooks:
	pre-commit run --all-files

.PHONY: format
format:
	autoflake --in-place --recursive --remove-all-unused-imports --remove-unused-variables --ignore-init-module-imports .
	ruff check --fix .
	black .
	isort .

.PHONY: lint
lint:
	ruff check .
	flake8 .
	pylint src/tomodachi_testcontainers tests
	mypy src tests
	mypy --config examples/pyproject.toml examples
	mypy --config docs_src/pyproject.toml docs_src
	bandit -r src examples
	pydocstringformatter --style=pep257 --style=numpydoc .

.PHONY: test
test:
	pytest -v

.PHONY: test-docs-src
test-docs-src:
	pytest -v docs_src

.PHONY: test-ci
test-ci:
	env TOMODACHI_TESTCONTAINER_EXPORT_COVERAGE=1 \
	pytest \
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
