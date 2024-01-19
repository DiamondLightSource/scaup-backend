FROM bitnami/postgresql:16-debian-11

WORKDIR /docker-entrypoint-initdb.d

ADD data.sql /docker-entrypoint-initdb.d/data.sql

ENV POSTGRESQL_PASSWORD sample_root
ENV POSTGRESQL_DATABASE sample_handling
ENV POSTGRESQL_USERNAME sample_handling

EXPOSE 5432
