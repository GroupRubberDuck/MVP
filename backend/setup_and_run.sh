#!/bin/sh

apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
curl -sSL https://install.python-poetry.org | python3 -
poetry install --no-root
poetry run flask --app backend.app:create_app run --debug --host 0.0.0.0