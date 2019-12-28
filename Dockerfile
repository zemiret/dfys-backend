# DEV Dockerfile.
FROM python:3.8

ENV PYTHONBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN pip install --upgrade pip
RUN pip install pipenv

RUN mkdir /app
WORKDIR /app

COPY Pipfile* /tmp/

RUN cd /tmp && \
	   pipenv lock -r > requirements.txt && \
	   pip install -r requirements.txt

RUN cd /tmp && \
	   pipenv lock -r -d > requirements-dev.txt && \
	   pip install -r requirements-dev.txt

COPY . /app/

ENV SETTINGS_CONFIG /app/dfys/dev.docker.env.json

