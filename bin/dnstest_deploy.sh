#!/usr/bin/env bash
set -e

ROOT=$(dirname "$0")
HELM_DIR="$ROOT/../helm_deploy/cla-public/"

helm upgrade cla-public \
  $HELM_DIR \
  --namespace=laa-cla-public-dnstest \
  --values ${HELM_DIR}/values-dnstest.yaml \
  --set host=laa-cla-public-dnstest.cloud-platform.service.justice.gov.uk \
  --set ingress.cluster.name=green \
  --set ingress.cluster.weight=100 \
  --set image.repository=$DOCKER_REPOSITORY \
  --set image.tag=$HARDCODED_IMAGE_TAG_IN_CONTEXT \
  --set-string pingdomIPs=$PINGDOM_IPS \
  --set-string sharedIPRangesLAA="Any IP allowed but keep this string" \
  --force \
  --install
