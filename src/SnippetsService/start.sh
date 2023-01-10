#! /bin/sh

nginx
gunicorn --bind unix:gunicorn.sock --workers 5 wsgi:app
