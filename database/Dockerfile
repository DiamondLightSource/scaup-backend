FROM mariadb:10.9.7-jammy

WORKDIR /docker-entrypoint-initdb.d

ENV MYSQL_ROOT_PASSWORD ispyb-root
ENV MYSQL_DATABASE ispyb
ENV MYSQL_USER ispyb
ENV MYSQL_PASSWORD ispyb-user

EXPOSE 3306

CMD ["mysqld"]