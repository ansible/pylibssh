#!/bin/bash
cd jenkins
docker build -t crypto-jenkins .
cd ../caddy
docker build -t caddy .
