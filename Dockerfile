# Verwende das offizielle Python-Image als Basis
FROM python:3.10

# Install opencv related libs
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get -y install tesseract-ocr tesseract-ocr-deu

# Setze das Arbeitsverzeichnis im Container
WORKDIR /usr/src/app

# Kopiere den restlichen Code der Anwendung in das Arbeitsverzeichnis
COPY . /usr/src/app

# Setze Umgebungsvariablen
# Python wird keine .pyc-Dateien im Container schreiben
ENV PYTHONDONTWRITEBYTECODE 1
# Python loggt direkt in die Konsole (hilfreich für das Debuggen mit Docker)
ENV PYTHONUNBUFFERED 1

# Installiere Python-Abhängigkeiten
# Kopiere zuerst nur die Requirements-Datei, um den Cache besser zu nutzen
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Create Log directory
RUN mkdir -p /usr/src/app/logs

# Execute collection of static files
RUN python manage.py collectstatic --noinput

COPY ./entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

# Port, auf dem der Container lauschen soll
EXPOSE 8000

# Führe den Befehl zum Starten von Gunicorn aus
CMD ["./entrypoint.sh"]
