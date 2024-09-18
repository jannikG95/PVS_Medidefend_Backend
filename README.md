## MediDefend Backend 

Medidefend ist ein umfassendes System, das die Kommunikation zwischen der PVS und ihren Kunden effektiv unterstützt. Dabei übernimmt Medidefend die Aufgabe, die Beanstandungen der Krankenversicherungen der Kunden sorgfältig zu analysieren. Auf Basis dieser Analyse prüft das System die Einwände und erstellt einen maßgeschneiderten Vorschlag für ein Antwortschreiben. Dadurch wird der gesamte Korrespondenzprozess erleichtert und effizienter gestaltet.

Dieses Repository enthält das Backend des Medidefend-Systems und bildet somit das technische Fundament für die reibungslose Funktionalität des gesamten Systems.


### Technologien

- **Frontend**: React
- **Backend**: Django (Python)
- **Datenbank**: Postgres
- **Deployment**: Docker & Docker Compose

### Voraussetzungen

Bevor Sie beginnen, stellen Sie sicher, dass Sie die folgenden Tools installiert haben:

- [Docker](https://www.docker.com/products/docker-desktop)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Anforderungen für die locale Nutzung außerhalb eines Docker Containers

Python >= 3.10

### Unterstützung

Bitte konsultieren Sie **<J:GEYER/> - IT Consulting & Development** oder die *issue page* und öffnen Sie ein Ticket.

### Schnellstart auf einem Server:

**1. Klonen des Repositories**
```bash
git clone git@github.com:jannikG95/PVS_Medidefend_Backend.git
```
Zudem muss das Medidefend-Frontend und die DataPipeline geklont werden.

**2. Docker-Netzwerk erstellen**

```bash
docker network create platform_network
```
Dieser Befehl erstellt ein Docker-Netzwerk, das für die Kommunikation der verschiedenen Container untereinander benötigt wird.


**2. Docker-Container erstellen und starten**
```bash
docker-compose -f docker-compose-prod.yml up --build
```
Mit diesem Befehl wird die Datenbank und das Backend in je einem Docker-Container gestartet. Die Option --build stellt sicher, dass alle Images neu gebaut werden.

### Lokaler Schnellstart:

1. docker network create platform_network // CREATE DOCKER NETWORK
2. docker-compose -f docker-compose-dev.yml up --build // DATABASE STARTUP
3. pip install -r requirements.txt // INSTALL PROJECT REQUIREMENTS
4. python manage.py makemigrations // CREATE MIGRATIONS
5. python manage.py migrate // EXECUTE MIGRATIONS
6. python manage.py createsuperuser // CREATE USER
7. python GOZ_extractor_2024.py ( in GOZ_Pipeline Repository ) // CREATES DB ENTRIES
8. python manage.py runserver // start application backend

**Öffnen der Anwendung**

Nachdem die Container erfolgreich gestartet wurden, ist Ihre Anwendung unter http://localhost:8001 erreichbar und kann über das Medidefend-Frontend angesprochen werden.

### Lizenz

Alle Rechte, einschließlich des Urheberrechts und anderer geistiger Eigentumsrechte an der Software "Medidefend" und zugehörigen Dokumentationen, liegen beim Unternehmen PVS/Limburg-Lahn GmbH.
Die Nutzung der Software, Dokumentationen und jeglicher damit verbundener Materialien wird Nutzern ausschließlich für den vorgesehenen Zweck unter den Bedingungen der hier genannten Lizenz gewährt. 
Jegliche andere Nutzung, Vervielfältigung, Verbreitung oder Bearbeitung der Software oder Teile davon ohne ausdrückliche schriftliche Zustimmung von PVS/Limburg-Lahn GmbH ist strengstens untersagt. Alle weiteren Rechte bleiben vorbehalten.