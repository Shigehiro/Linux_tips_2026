# Run PowerDNS, PowerDNS-Admin (GUI), and PowerAdmin (GUI) with Docker | Podman-Compose

## Description

[This Compose setup](./compose.yml) launches one primary PowerDNS instance, one backend database (PostgreSQL), one PowerDNS-Admin (GUI), and one PowerAdmin (GUI) in a containerized environment for evaluation purposes. It is useful for assessing both GUI applications.

## About PowerDNS-Admin, poweradmin

There are two GUI-based applications for managing PowerDNS:

- [PowerDNS-Admin](https://github.com/PowerDNS-Admin/PowerDNS-Admin)
- [poweradmin](https://github.com/poweradmin/poweradmin)

## How to run cantainers

Run the containers. The PowerAdmin container will fail to start because the required tables are missing in the database.
```
podman-compose -f compose.yml up -d
```

<br>Copy th sql file to the postgresql container.<br>
You can find the sql file from https://github.com/poweradmin/poweradmin/tree/master/sql
```
 podman cp ./poweradmin-pgsql-db-structure.sql run_powerdns_powerdnsadmin_poweradmin_postgres_1:/
```

<br>Load the sql file.
```
$ podman exec -it run_powerdns_powerdnsadmin_poweradmin_postgres_1 bash

f87802be080d:/# psql -U postgres -d powerdns < poweradmin-pgsql-db-structure.sql

f87802be080d:/# exit
```

<br>Start the poweradmin container.
```
podman restart run_powerdns_powerdnsadmin_poweradmin_poweradmin_1
```

<br>Confirm all containers are up and running.
```
$ podman-compose -f compose.yml ps
CONTAINER ID  IMAGE                                   COMMAND               CREATED        STATUS                  PORTS                                             NAMES
f87802be080d  docker.io/library/postgres:18-alpine    postgres              3 minutes ago  Up 3 minutes (healthy)  5432/tcp                                          run_powerdns_powerdnsadmin_poweradmin_postgres_1
575312d1a1c4  docker.io/library/adminer:latest        php -S [::]:8080 ...  3 minutes ago  Up 3 minutes            0.0.0.0:7988->8080/tcp                            run_powerdns_powerdnsadmin_poweradmin_adminer_1
ace54b5dad14  docker.io/pschiffe/pdns-pgsql:latest    /usr/sbin/pdns_se...  3 minutes ago  Up 3 minutes            53/tcp, 53/udp                                    run_powerdns_powerdnsadmin_poweradmin_pdns-pgsql-master_1
ab9dd25102d6  docker.io/pschiffe/pdns-admin:latest    /usr/bin/supervis...  3 minutes ago  Up 3 minutes            0.0.0.0:7989->8080/tcp                            run_powerdns_powerdnsadmin_poweradmin_pdns-admin-pgsql_1
8cb612821aa3  docker.io/poweradmin/poweradmin:latest  frankenphp run --...  3 minutes ago  Up About a minute       0.0.0.0:7990->80/tcp, 443/tcp, 2019/tcp, 443/udp  run_powerdns_powerdnsadmin_poweradmin_poweradmin_1
```

<br>To access PowerDNS-Admin, navigate to: http://[docker-host-ip]:7989<br>
To access PowerAdmin, navigate to: http://[docker-host-ip]:7990<br>
You can add zones and resource records (RRs) using either GUI.
Any configuration changes will be reflected in the other GUI.