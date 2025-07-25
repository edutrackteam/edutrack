#!/usr/bin/env bash
# exit on error
set -o errexit

# poetry install
# pip install -r requirements.txt

py manage.py collectstatic --no-input
py manage.py migrate