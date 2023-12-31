FROM python:3.11.4-slim-buster AS python-base
WORKDIR /app
ARG VIRTUAL_ENV=/opt/venv
RUN addgroup --gid 1001 app && adduser --uid 1000 --gid 1001 app
ENV VIRTUAL_ENV=$VIRTUAL_ENV \
  PATH=$VIRTUAL_ENV/bin:$PATH \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONBUFFERED=1 \
  PYTHONPATH=/app/src:$PYTHONPATH

FROM python-base AS dependencies-base
ARG PIP_VERSION=23.3.1
ARG POETRY_VERSION=1.7.1
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
CMD ["tomodachi", "run", "src/healthcheck.py", "--loop", "uvloop"]

FROM dependencies-base AS test
RUN poetry install --with test
COPY --link . .
RUN poetry install --with test
CMD ["tomodachi", "run", "src/healthcheck.py", "--loop", "uvloop", "--production"]

FROM python-base AS release
COPY --link --from=dependencies-release --chown=app:app /opt/venv /opt/venv
COPY --link --from=dependencies-release --chown=app:app /app .
USER app
CMD ["tomodachi", "run", "src/healthcheck.py", "--loop", "uvloop", "--production"]
