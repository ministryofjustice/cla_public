#!/usr/bin/env bash
set -e

ROOT=$(dirname "$0")
NAMESPACE="development"
NAMESPACE_DIR="$ROOT/../kubernetes_deploy/$NAMESPACE"

kubectl config use-context docker-for-desktop

ECR_DEPLOY_IMAGE=cla_public_local .circleci/deploy_to_kubernetes $NAMESPACE
