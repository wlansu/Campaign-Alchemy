# syntax=docker/dockerfile:1
FROM python:3.11
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin:$PATH"
WORKDIR /code
RUN pip3 install --upgrade pip
RUN curl -sSL https://install.python-poetry.org | python3 -

COPY poetry.lock pyproject.toml /code/

RUN poetry config virtualenvs.create false
RUN poetry install --sync
COPY . /code/

# Expose port used for django server
EXPOSE 8000

# Run server entrypoint
ENTRYPOINT ["/code/entrypoint.sh"]
