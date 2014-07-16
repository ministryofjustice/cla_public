#!/bin/bash
CLA_DOCKER_REGISTRY=docker.cla.dsd.io
sudo docker build --force-rm=true -t $CLA_DOCKER_REGISTRY/$APP_NAME .
sudo docker tag $CLA_DOCKER_REGISTRY/$APP_NAME $CLA_DOCKER_REGISTRY/$APP_NAME:$GIT_COMMIT 
sudo docker push $CLA_DOCKER_REGISTRY/$APP_NAME
