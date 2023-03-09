#!/bin/sh

nginx
gunicorn --bind unix:gunicorn.sock --workers 3 wsgi:app
