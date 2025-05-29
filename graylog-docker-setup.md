# Graylog docker setup on RedHat/Centos/Ubuntu
<!-- TOC -->

- [Graylog docker setup on RedHat/Centos/Ubuntu](#graylog-docker-setup-on-redhatcentosubuntu)
    - [Docker Setup](#docker-setup)
    - [Debugging docker issues](#debugging-docker-issues)
        - [Ensure containers are running](#ensure-containers-are-running)
        - [Some examples of getting logs to debug issues](#some-examples-of-getting-logs-to-debug-issues)
        - [Log time format issues](#log-time-format-issues)
    - [Update graylog containers](#update-graylog-containers)
    - [Teardown app and cleanup data](#teardown-app-and-cleanup-data)

<!-- /TOC -->
## Docker Setup 
1. Modify the docker compose file in the source pack. <br>
(Orig source should you need it: https://github.com/Graylog2/docker-compose/blob/main/open-core/docker-compose.yml)
2. add udp ports per host for syslog inputs in the graylog service section of the compose file
have a look at [docker-compose.yaml](docker-compose.yaml)
Ex:
```
# host1
- "5141:5141/udp"
# host2
- "5142:5142/udp"
# firewall host
- "5143:5143/udp"
```
3. install pwgen
```
sudo apt install pwgen
or
sudo yum install pwgen
```
4. generate random string for GRAYLOG_PASSWORD_SECRET, store in variable, replace in compose file<br>
**note leave space in front of next command so plaintext secret doesn't go into shell history**
```
 export randomstring=$(pwgen -N 1 -s 96)
sed -i 's/GRAYLOG_PASSWORD_SECRET:.*/GRAYLOG_PASSWORD_SECRET: "'$randomstring'"/g' docker-compose.yaml
unset randomstring
```
5. hash the root(web UI: admin, not os) password and replace GRAYLOG_ROOT_PASSWORD_SHA2 value in compose file<br>
**note leave space in front of next command so plaintext pw doesn't go into shell history**
```
 export graylogadminpw=$(echo -n <somecomplexpasswordgoeshere> | shasum -a 256)
sed -i 's/GRAYLOG_ROOT_PASSWORD_SHA2:.*/GRAYLOG_ROOT_PASSWORD_SHA2: "'$graylogadminpw'"/g' docker-compose.yaml
unset graylogadminpw
```
7. configure virtual memory mmap count to prevent out of memory exceptions on the docker host
```
sudo sysctl -w vm.max_map_count=262144
echo 'vm.max_map_count=262144' | sudo tee -a /etc/sysctl.conf
```
8. Launch container, volume, network stack
```
docker compose up -d
```
9. Get initial web UI pw and login to app from browser
```
docker logs graylog-graylog-1 | grep -oP "password '\K[^']+"
```
Login to web UI username: admin (onetime pw from previous step) . Configue CA or add your own. <br>
Once full web UI comes up recommend also do the following:
- turn off telemetry for admin user in UI
- create api token for admin user in UI for using swagger REST API

## Debugging docker issues
### Ensure containers are running
```
docker ps --filter name=graylog --format "table {{.ID}}\t{{.Names}}\t{{.Status}}"

CONTAINER ID   NAMES                STATUS
71b250c9ea6c   graylog-graylog-1    Up 47 hours (healthy)
5f06701c92a8   graylog-datanode-1   Up 47 hours
32d2f0d336cf   graylog-mongodb-1    Up 47 hours
```
### Some examples of getting logs to debug issues
```
docker logs graylog-graylog-1 | grep ERROR
docker logs graylog-datanode-1 | grep WARN
docker logs graylog-mongodb-1 
docker logs --tail 10 graylog-graylog-1 | grep INFO
```
### Log time format issues
Lots of containers use UTC. In the compose file we modify the admin's timezone display for server.
This cannot be "easily" done for the datanode or mongo.
It can be a challenge to correlate events between containers based on timestamps.
This requires scripting with sed/awk etc. Examples to come in future updates.

## Update graylog containers
```
docker compose down
docker pull graylog/graylog:6.2
docker pull graylog/graylog-datanode:6.2
docker compose up -d
```

## Teardown app and cleanup data
```
docker compose down
docker volume rm $(docker volume ls -q | grep graylog)
```

