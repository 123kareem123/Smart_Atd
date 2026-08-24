#!/usr/bin/env bash
set -o errexit

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py create_departments
python manage.py import_subjects
python manage.py setup_demo