#!/usr/bin/env bash
set -e

ROOT=$(dirname "$0")
HELM_DIR="$ROOT/../helm_deploy/cla-public/"

# Pull ranges from shared LAA IP ranges and then remove spaces,
# replace linebreaks with commas, remove last comma, and escape commas for helm input 
SHARED_IP_RANGES_LAA=$(curl -s https://raw.githubusercontent.com/ministryofjustice/laa-ip-allowlist/main/cidrs.txt | tr -d ' ' | tr '\n' ',' | sed 's/,/\\,/g' | sed 's/\\,$//')

helm upgrade $CLEANED_BRANCH_NAME \
  $HELM_DIR \
  --namespace=${KUBE_ENV_STAGING_NAMESPACE} \
  --values ${HELM_DIR}/values-staging.yaml \
  --set fullnameOverride=$CLEANED_BRANCH_NAME \
  --set environment=$CLEANED_BRANCH_NAME \
  --set host=$CLEANED_BRANCH_NAME.$STAGING_HOST \
  --set ingress.cluster.name=${INGRESS_CLUSTER_NAME} \
  --set ingress.cluster.weight=${INGRESS_CLUSTER_WEIGHT} \
  --set ingress.secretName=tls-wildcard-certificate \
  --set image.repository=$DOCKER_REPOSITORY \
  --set image.tag=$IMAGE_TAG \
  --set dashboard.enabled=false \
  --set-string pingdomIPs=$PINGDOM_IPS \
  --set-string sharedIPRangesLAA=$SHARED_IP_RANGES_LAA \
  --force \
  --install
