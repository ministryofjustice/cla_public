#!/usr/bin/env bash
set -e

ROOT=$(dirname "$0")
HELM_DIR="$ROOT/../helm_deploy/cla-backend/"

kubectl config use-context docker-for-desktop

helm upgrade cla-backend \
  $HELM_DIR \
  --values ${HELM_DIR}/values-dev.yaml \
  --install
