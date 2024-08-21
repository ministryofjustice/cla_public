#!/usr/bin/env bash
set -e

ROOT=$(dirname "$0")
HELM_DIR="$ROOT/../helm_deploy/cla-public/"

SHARED_IP_RANGES_LAA=$(curl -s https://raw.githubusercontent.com/ministryofjustice/laa-ip-allowlist/main/cidrs.txt | tr -d ' ' | tr '\n' ',' | sed 's/,/\\,/g' | sed 's/\\,$//')

helm upgrade cla-public \
  $HELM_DIR \
  --namespace=${KUBE_ENV_STAGING_NAMESPACE} \
  --values ${HELM_DIR}/values-staging.yaml \
  --set host=$STAGING_HOST \
  --set ingress.cluster.name=${INGRESS_CLUSTER_NAME} \
  --set ingress.cluster.weight=${INGRESS_CLUSTER_WEIGHT} \
  --set image.repository=$DOCKER_REPOSITORY \
  --set image.tag=$IMAGE_TAG \
  --set-string pingdomIPs=$PINGDOM_IPS \
  --set-string sharedIPRangesLAA=$SHARED_IP_RANGES_LAA \
  --force \
  --install
