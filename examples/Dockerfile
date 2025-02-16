FROM python:3.13.2-bookworm AS python-base
WORKDIR /app
ARG VIRTUAL_ENV=/opt/venv
RUN addgroup --system --gid 1001 app && adduser --system --uid 1001 --gid 1001 app
ENV VIRTUAL_ENV=$VIRTUAL_ENV \
  PATH=$VIRTUAL_ENV/bin:$PATH \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONBUFFERED=1 \
  PYTHONPATH=/app/src

FROM python-base AS dependencies-base
ARG PIP_VERSION=25.0
ARG POETRY_VERSION=2.1.0
RUN python -m pip install --no-cache-dir -U \
  "pip==$PIP_VERSION" \
  "poetry==$POETRY_VERSION" && \
  virtualenv "$VIRTUAL_ENV"
COPY --link pyproject.toml poetry.lock ./
RUN poetry install

FROM dependencies-base AS dependencies-release
COPY --link src ./src
RUN poetry install

FROM dependencies-base AS dev
RUN poetry install --with dev
COPY --link . .
RUN poetry install --with dev

FROM dependencies-base AS test
RUN poetry install --with test
COPY --link . .
RUN poetry install --with test
USER app

FROM python-base AS release
COPY --link --from=dependencies-release --chown=1001:1001 /opt/venv /opt/venv
COPY --link --from=dependencies-release --chown=1001:1001 /app .
USER app
