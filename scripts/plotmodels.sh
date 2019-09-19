#!/bin/bash
# This is a useful script to plot your db diagram.
# Before executing:
# 1. add 'django_extensions' to installed apps!
# 2. workon test

python ../manage.py graph_models -a -g -o models.png && xdg-open models.png

