FROM python:3 

ENV PYTHONBUFFERED 1

RUN pip install --upgrade pip
RUN pip install pipenv

RUN mkdir /app
WORKDIR /app

COPY Pipfile* /tmp/
RUN cd /tmp && \
	   pipenv lock --requirements > requirements.txt && \
	   pip install -r requirements.txt

COPY . /app/

