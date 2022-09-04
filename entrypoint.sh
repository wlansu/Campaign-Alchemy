#!/bin/sh

if [ -z "${POSTGRES_USER}" ]; then
    base_postgres_image_default_user='postgres'
    export POSTGRES_USER="${base_postgres_image_default_user}"
fi
export DATABASE_URL="postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"

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
#python manage.py collectstatic --noinput --verbosity 0

echo "Populating database"
#python manage.py resetdb

if [ $# = 0 ]
then
  echo "Assuming execution from shell. Starting Django server"
  python manage.py runserver 0.0.0.0:8000
else
  echo "Assuming execution from IDE. Running provided commands"
  exec "$@"
fi
