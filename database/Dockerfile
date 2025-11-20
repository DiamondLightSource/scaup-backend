FROM postgres:17.6

WORKDIR /docker-entrypoint-initdb.d

# Dummy data
ADD data.sql /docker-entrypoint-initdb.d/data.sql

ENV POSTGRES_PASSWORD sample_root
ENV POSTGRES_DB sample_handling
ENV POSTGRES_USER sample_handling

EXPOSE 5432
