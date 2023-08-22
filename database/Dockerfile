FROM mariadb:10.9.7-jammy

WORKDIR /docker-entrypoint-initdb.d

ADD data.sql /docker-entrypoint-initdb.d/data.sql

ENV MYSQL_ROOT_PASSWORD sample_root
ENV MYSQL_DATABASE sample_handling
ENV MYSQL_USER sample_handling
ENV MYSQL_PASSWORD sample_handling
ENV MYSQL_TCP_PORT 3666

EXPOSE 3666

CMD ["mysqld"]