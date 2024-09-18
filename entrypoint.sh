#!/bin/bash

# Stoppe die Ausführung bei Fehlern
set -e

# Führe Datenbankmigrationen aus
python manage.py makemigrations
python manage.py migrate

# Erstelle einen Superuser, falls er noch nicht existiert
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()

# Liste der Benutzer, die erstellt werden sollen
users = [
    {"username": "malenegoerg", "email": "m.goerg@pvs-dental.de", "password": "sCan3D5bRmPxH8LjbBaB"},
    {"username": "anjaschmidt", "email": "a.schmidt@pvs-dental.de", "password": "YD2o2NzDYnHwcp2nj13m"},
    {"username": "andreautta", "email": "a.utta@pvs-dental.de", "password": "qpZ4Er3N352FXTMN27iA"}
]

for user in users:
    if not User.objects.filter(username=user['username']).exists():
        User.objects.create_superuser(user['username'], user['email'], user['password'])
        print(f"Superuser '{user['username']}' wurde erstellt.")
    else:
        print(f"Superuser '{user['username']}' existiert bereits.")
EOF

# Starte den Gunicorn-Server
exec gunicorn --bind 0.0.0.0:8000 pvs_backend.wsgi:application