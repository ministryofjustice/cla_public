#!/usr/bin/env bash
set -e

ROOT=$(dirname "$0")
HELM_DIR="$ROOT/../helm_deploy/cla-public/"

docker build -t cla_public_local "$ROOT/.."

kubectl config use-context docker-for-desktop

helm upgrade cla-public \
  $HELM_DIR \
  --values ${HELM_DIR}/values-dev.yaml \
  --force \
  --install
