FROM python:3.10-slim-buster

LABEL maintainer="nlp@thedeep.io"

ENV PYTHONUNBUFFERED 1

WORKDIR /code

RUN apt-get update -y && \
    apt-get install ffmpeg libsm6 libxext6 -y && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock /code/

# Upgrade pip and install python packages for code
RUN pip install --upgrade --no-cache-dir pip poetry \
    && poetry --version \
    # Configure to use system instead of virtualenvs
    && poetry config virtualenvs.create false \
    && poetry install --no-root \
    # Remove installer
    && pip uninstall -y poetry virtualenv-clone virtualenv

COPY . /code/