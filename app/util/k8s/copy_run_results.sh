#!/usr/bin/env bash

DCAPT_DOCKER_IMAGE="atlassian/dcapt"
echo "INFO: DCAPT docker image: $DCAPT_DOCKER_IMAGE"

if [[ -z "$ENVIRONMENT_NAME" ]]; then
  echo "ERROR: ENVIRONMENT_NAME variable is not set."
  exit 1
fi
echo "INFO: Environment name: $ENVIRONMENT_NAME"

if [[ -z "$REGION" ]]; then
  echo "ERROR: REGION variable is not set."
  exit 1
fi
echo "INFO: AWS REGION: $REGION"

echo "INFO: Update kubeconfig"
aws eks update-kubeconfig --name atlas-"$ENVIRONMENT_NAME"-cluster --region "$REGION"

echo "INFO: Get execution environment pod name"
exec_pod_name=$(kubectl get pods -n atlassian -l=exec=true --no-headers -o custom-columns=":metadata.name")

if [[ -z "$exec_pod_name" ]]; then
  echo "ERROR: Current cluster does not have execution environment pod. Check what environment type is used.
  Development environment does not have execution environment pod by default because dedicated for local app-specific actions development only."
  exit 1
fi

echo "INFO: Execution environment pod name: $exec_pod_name"

echo "INFO: Copy results folder from the exec env pod to local"
# Ensure the local results directory exists
local_results_dir="/data-center-terraform/dc-app-performance-toolkit/app/results"
mkdir -p "$local_results_dir"

for _ in {1..3}; do
    if kubectl exec -n atlassian "$exec_pod_name" --request-timeout=60s -- tar czf - -C /dc-app-performance-toolkit/app results | tar xzf - -C "$local_results_dir" --strip-components=1; then
        break
    else
        echo "Copying failed, retrying..."
        sleep 5
    fi
done

if [[ $? -ne 0 ]]; then
    echo "ERROR: Copy results folder failed"
    exit 1
fi