#!/bin/bash
export DOCKER_BUILDKIT=1
export ENVIRONMENT=${1:-development}
echo "running environment $ENVIRONMENT"
docker-compose down --remove-orphans
docker-compose up --build
