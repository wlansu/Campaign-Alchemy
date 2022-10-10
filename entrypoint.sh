#!/bin/sh

echo "Running Django migrations"
python manage.py makemigrations --noinput --verbosity 0
if [ $? -eq 3 ]
then
  echo "User input needed for makemigrations command" >&2
  exit 1
fi

set -e

python manage.py migrate --noinput --verbosity 0

echo "Collecting static files"
python manage.py collectstatic --noinput --verbosity 0

echo "Compressing files"
python manage.py compress --noinput --verbosity 0

if [ $# = 0 ]
then
  echo "Assuming execution from shell. Starting Django server"
  python manage.py runserver 0.0.0.0:8000
else
  echo "Assuming execution from IDE. Running provided commands"
  exec "$@"
fi
