#!/bin/bash
CLA_DOCKER_REGISTRY=docker.cla.dsd.io
sudo docker build --force-rm=true -t docker.cla.dsd.io/$APP_NAME .
sudo docker tag docker.cla.dsd.io/$APP_NAME docker.cla.dsd.io/$APP_NAME:$GIT_COMMIT 
sudo docker push docker.cla.dsd.io/$APP_NAME
