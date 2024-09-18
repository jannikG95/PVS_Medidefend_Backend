SETUP 

DEV

1. docker network create platform_network // CREATE DOCKER NETWORK
2. docker-compose -f docker-compose-dev.yml up --build // DATABASE STARTUP
3. pip install -r requirements.txt // INSTALL PROJECT REQUIREMENTS
4. python manage.py makemigrations // CREATE MIGRATIONS
5. python manage.py migrate // EXECUTE MIGRATIONS
6. python manage.py createsuperuser // CREATE USER
7. python GOZ_extractor.py ( in GOZ_Pipeline Repository ) // CREATES DB ENTRIES
8. python manage.py runserver // start application backend

CREATE BACKUP

docker exec container bash -c "pg_dump -U user -F t -f /filename.tar -t tablename database"

LOAD BACKUP

docker exec container pg_restore -U user -d database --clean -v filename.tar
