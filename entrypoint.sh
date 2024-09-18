#!/bin/bash

# Stoppe die Ausführung bei Fehlern
set -e

# Führe Datenbankmigrationen aus
python manage.py makemigrations
python manage.py migrate

# Starte den Gunicorn-Server
exec gunicorn --bind 0.0.0.0:8000 pvs_backend.wsgi:application
