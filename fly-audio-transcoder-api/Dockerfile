FROM python:3.11-bookworm as poetry
ENV POETRY_VERSION=1.5.1
RUN curl -sSL https://install.python-poetry.org | python
WORKDIR /app

FROM python:3.11-bookworm as venv
COPY --from=poetry /root/.local /root/.local
ENV PATH /root/.local/bin:$PATH
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN python -m venv --copies /app/venv && \
    . /app/venv/bin/activate && \
    poetry install --no-root

FROM python:3.11-slim-bookworm as prod
WORKDIR /app
COPY --from=venv /app/venv /app/venv/
ENV PATH /app/venv/bin:$PATH
COPY ./fly_audio_transcoder_api /app/fly_audio_transcoder_api
CMD ["gunicorn", "fly_audio_transcoder_api.main:app", "--workers", "5", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "[::]:8080"]