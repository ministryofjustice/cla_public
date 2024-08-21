#!/usr/bin/env bash
set -e

ROOT=$(dirname "$0")
HELM_DIR="$ROOT/../helm_deploy/cla-public/"

helm upgrade cla-public \
  $HELM_DIR \
  --namespace=${KUBE_ENV_PRODUCTION_NAMESPACE} \
  --values ${HELM_DIR}/values-production.yaml \
  --set host=$PRODUCTION_HOST \
  --set ingress.cluster.name=${INGRESS_CLUSTER_NAME} \
  --set ingress.cluster.weight=${INGRESS_CLUSTER_WEIGHT} \
  --set image.repository=$DOCKER_REPOSITORY \
  --set image.tag=$IMAGE_TAG \
  --set-string pingdomIPs=$PINGDOM_IPS \
  --set-string sharedIPRangesLAA="Any IP allowed but keep this string" \
  --force \
  --install
