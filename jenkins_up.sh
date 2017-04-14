#!/bin/bash

docker run -d -p 50000:50000 -v /var/run/docker.sock:/var/run/docker.sock -v jenkins_home:/var/jenkins_home --name jenkins crypto-jenkins
# The mount to /root/.caddy is just to cache certs
docker run -d -p 443:443 -p 80:80 --link jenkins:jenkins -v /caddy:/root/.caddy --name caddy caddy
