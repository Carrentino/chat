FROM python:3.12

# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-client \
    git && \
    rm -rf /var/lib/apt/lists/*

# Настройка SSH
RUN mkdir -p /root/.ssh && chmod 0700 /root/.ssh && \
    touch /root/.ssh/known_hosts && \
    ssh-keyscan -H bitbucket.org >> /root/.ssh/known_hosts

WORKDIR /app

RUN pip install --no-cache-dir pip==24.3.1 setuptools==75.6.0 wheel==0.45.1 && \
    pip install --no-cache-dir poetry==1.8.2

COPY pyproject.toml poetry.lock alembic.ini ./
COPY src src

RUN --mount=type=ssh poetry install --no-cache -vvv --only main

CMD ["poetry", "run", "python", "src/main.py"]
