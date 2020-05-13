#!/usr/bin/env bash
set -e

ROOT=$(dirname "$0")
HELM_DIR="$ROOT/../helm_deploy/cla-public/"

helm upgrade cla-public \
  $HELM_DIR \
  --namespace=${KUBE_ENV_PRODUCTION_NAMESPACE} \
  --values ${HELM_DIR}/values-production.yaml \
  --set host=$PRODUCTION_HOST \
  --set image.repository=$DOCKER_REPOSITORY \
  --set image.tag=$IMAGE_TAG \
  --force \
  --install