#!/bin/sh
set -e

echo "Waiting for postgres at $POSTGRES_HOST:$POSTGRES_PORT..."

until nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
  sleep 1
done

echo "Postgres is up - running migrations..."
python manage.py migrate --noinput

echo "Starting server..."
exec "$@"
