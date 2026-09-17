FROM postgres:15-alpine

ENV POSTGRES_DB=dietitian_db
ENV POSTGRES_USER=black
ENV POSTGRES_PASSWORD=12345

COPY dietitainDB.sql /docker-entrypoint-initdb.d/init.sql

EXPOSE 5432
