FROM bitnami/postgresql:17-debian-12

WORKDIR /docker-entrypoint-initdb.d

# Dummy data
ADD data.sql /docker-entrypoint-initdb.d/data.sql

ENV POSTGRESQL_PASSWORD sample_root
ENV POSTGRESQL_DATABASE sample_handling
ENV POSTGRESQL_USERNAME sample_handling

EXPOSE 5432
