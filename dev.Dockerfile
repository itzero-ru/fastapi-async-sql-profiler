# Используем официальный образ Python
FROM python:3.12
# FROM python:3.13.0

#RUN apt-get update && apt-get install -y build-essential
# RUN apt-get update && apt-get install -y build-essential
# RUN apt-get update \
#     && apt-get dist-upgrade -y \
#     && apt-get install --no-install-recommends -yq \
#     gcc \
#     g++ \
#     libc-dev \
#     libpq-dev \
#     make

WORKDIR /app
RUN pip install poetry
# install requirements into a separate layer
COPY poetry.lock pyproject.toml /app/
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi

COPY . ./app