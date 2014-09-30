#!/bin/bash
set -e
CLA_DOCKER_REGISTRY=docker.cla.dsd.io

[[ $(curl -o /dev/null --silent --head --write-out '%{http_code}\n' http://$CLA_DOCKER_REGISTRY/v1/repositories/$APP_NAME/images) == '200' ]] || { echo -e "\n$(tput setaf 1)THE DOCKER REGISTRY IS DOWN!$(tput sgr0)"; exit 1; }

sudo docker build --force-rm=true -t $CLA_DOCKER_REGISTRY/$APP_NAME .
sudo docker tag $CLA_DOCKER_REGISTRY/$APP_NAME $CLA_DOCKER_REGISTRY/$APP_NAME:$GIT_COMMIT 
sudo docker push $CLA_DOCKER_REGISTRY/$APP_NAME || sleep 1 && sudo docker push $CLA_DOCKER_REGISTRY/$APP_NAME
