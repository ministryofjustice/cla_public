#!/usr/bin/env bash
set -e

ROOT=$(dirname "$0")
HELM_DIR="$ROOT/../helm_deploy/cla-public/"

helm upgrade $RELEASE_NAME \
  $HELM_DIR \
  --namespace=${KUBE_ENV_STAGING_NAMESPACE} \
  --values ${HELM_DIR}/values-staging.yaml \
  --set fullnameOverride=$RELEASE_NAME \
  --set host=$RELEASE_HOST \
  --set image.repository=$DOCKER_REPOSITORY \
  --set image.tag=$IMAGE_TAG \
  --force \
  --install