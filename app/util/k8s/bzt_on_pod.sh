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

if [ $# -eq 0 ]; then
  echo "ERROR: No arguments supplied. Product .yml file need to be passed as argument. E.g. jira.yml"
  exit 1
fi
echo "INFO: Product .yml: $1"

echo "INFO: Update kubeconfig"
aws eks update-kubeconfig --name atlas-"$ENVIRONMENT_NAME"-cluster --region "$REGION"

echo "INFO: Get execution environment pod name"
exec_pod_name=$(kubectl get pods -n atlassian -l=exec=true --no-headers -o custom-columns=":metadata.name")
echo "INFO: Execution environment pod name: $exec_pod_name"

echo "INFO: Cleanup dc-app-performance-toolkit folder on the exec env pod"
kubectl exec -it "$exec_pod_name" -n atlassian -- rm -rf /dc-app-performance-toolkit

echo "INFO: Copy latest dc-app-performance-toolkit folder to the exec env pod"
kubectl cp --retries 10 dc-app-performance-toolkit atlassian/"$exec_pod_name":/dc-app-performance-toolkit

echo "INFO: Run bzt on the exec env pod"
kubectl exec -it "$exec_pod_name" -n atlassian -- docker run --pull=always --shm-size=4g -v "/dc-app-performance-toolkit:/dc-app-performance-toolkit" $DCAPT_DOCKER_IMAGE "$1"
sleep 10

echo "INFO: Copy results folder from the exec env pod to local"
kubectl cp --retries 10 atlassian/"$exec_pod_name":dc-app-performance-toolkit/app/results dc-app-performance-toolkit/app/results
if [[ $? -ne 0 ]]; then
    echo "ERROR: Copy results folder failed"
    exit 1
fi