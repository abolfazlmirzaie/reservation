#!/bin/sh


echo "Running migrations"


pyhton manage.py migrate

echo "Starting"

exec "$@"