#!/bin/sh
python manage.py collectstatic --noinput
python manage.py migrate

# python -m uvicorn --port 8000 config.asgi:application
python -m gunicorn -b 0.0.0.0:8000 -k uvicorn.workers.UvicornWorker config.asgi:application
