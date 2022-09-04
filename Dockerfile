# syntax=docker/dockerfile:1
FROM python:3.10-slim-bullseye
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin:$PATH"
WORKDIR /code
RUN apt-get update && apt-get -y install curl
RUN pip install --upgrade pip
RUN curl -sSL https://install.python-poetry.org | python3 -

COPY poetry.lock pyproject.toml /code/

RUN poetry config virtualenvs.create false
RUN poetry install --sync
COPY . /code/
