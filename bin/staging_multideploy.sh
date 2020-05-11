#!/usr/bin/env bash
set -e

ROOT=$(dirname "$0")
HELM_DIR="$ROOT/../helm_deploy/cla-public/"

helm upgrade $CLEANED_BRANCH_NAME \
  $HELM_DIR \
  --namespace=${KUBE_ENV_STAGING_NAMESPACE} \
  --values ${HELM_DIR}/values-staging.yaml \
  --set fullnameOverride=$CLEANED_BRANCH_NAME \
  --set host=$CLEANED_BRANCH_NAME.$STAGING_HOST \
  --set ingress.secretName=tls-wildcard-certificate \
  --set image.repository=$DOCKER_REPOSITORY \
  --set image.tag=$IMAGE_TAG \
  --set dashboard.enabled=false \
  --force \
  --install