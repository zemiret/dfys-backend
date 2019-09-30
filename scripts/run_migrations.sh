#!/bin/bash

docker-compose run app python manage.py makemigrations
docker-compose run app python manage.py migrate 
