#!/bin/bash

pushd jenkins
docker build -t crypto-jenkins .
popd

pushd caddy
docker build -t caddy .
popd
