#!/bin/sh


echo "Running migrations"


pyhton manage.py makemigrations
pyhton manage.py migrate

echo "Starting"

exec "$@"