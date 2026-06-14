FROM python:3.14.6-bookworm AS python-base
WORKDIR /app
ARG VIRTUAL_ENV=/opt/venv
RUN addgroup --system --gid 1001 app && adduser --system --uid 1001 --gid 1001 app
ENV VIRTUAL_ENV=$VIRTUAL_ENV \
  PATH=$VIRTUAL_ENV/bin:$PATH \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONBUFFERED=1 \
  PYTHONPATH=/app/src

FROM python-base AS dependencies-base
COPY --from=ghcr.io/astral-sh/uv:0.11.21 /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 \
  UV_LINK_MODE=copy \
  UV_PROJECT_ENVIRONMENT=$VIRTUAL_ENV
COPY --link pyproject.toml uv.lock ./
RUN uv sync --frozen --no-default-groups

FROM dependencies-base AS dependencies-release
COPY --link src ./src
RUN uv sync --frozen --no-default-groups

FROM dependencies-base AS dev
RUN uv sync --frozen --no-default-groups --group dev
COPY --link . .
RUN uv sync --frozen --no-default-groups --group dev

FROM dependencies-base AS test
RUN uv sync --frozen --no-default-groups --group test
COPY --link . .
RUN uv sync --frozen --no-default-groups --group test
USER app

FROM python-base AS release
COPY --link --from=dependencies-release --chown=1001:1001 /opt/venv /opt/venv
COPY --link --from=dependencies-release --chown=1001:1001 /app .
USER app
