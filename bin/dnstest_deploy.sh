#!/usr/bin/env bash
set -e

ROOT=$(dirname "$0")
HELM_DIR="$ROOT/../helm_deploy/cla-public/"

# Pull ranges from shared LAA IP ranges and then remove spaces,
# replace linebreaks with commas, remove last comma, and escape commas for helm input 
SHARED_IP_RANGES_LAA=$(curl -s https://raw.githubusercontent.com/ministryofjustice/laa-ip-allowlist/main/cidrs.txt | tr -d ' ' | tr '\n' ',' | sed 's/,/\\,/g' | sed 's/\\,$//')

helm upgrade cla-public \
  $HELM_DIR \
  --namespace=laa-cla-public-dnstest \
  --values ${HELM_DIR}/values-dnstest.yaml \
  --set host=dnstest.checklegalaid.service.gov.uk \
  --set ingress.cluster.name=green \
  --set ingress.cluster.weight=100 \
  --set image.repository=$DOCKER_REPOSITORY \
  --set image.tag=$HARDCODED_IMAGE_TAG_IN_CONTEXT \
  --set-string pingdomIPs=$PINGDOM_IPS \
  --set-string sharedIPRangesLAA=$SHARED_IP_RANGES_LAA \
  --force \
  --install
