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
  echo "ERROR: No arguments supplied. Product .yml file need to be passed as first argument. E.g. jira.yml"
  exit 1
fi

if [[ $1 =~ "yml" ]]; then
  echo "INFO: Product .yml: $1"
else
  echo "ERROR: first argument should be product.yml, e.g. jira.yml"
  echo "ERROR: provided first argument: $1"
  exit 1
fi


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

echo "INFO: Cleanup dc-app-performance-toolkit folder on the exec env pod"
kubectl exec -it "$exec_pod_name" -n atlassian -- rm -rf /dc-app-performance-toolkit

echo "INFO: Copy latest dc-app-performance-toolkit folder to the exec env pod"
start=$(date +%s)
# tar only app folder, exclude results and util/k8s folder
tar -czf dcapt.tar.gz -C dc-app-performance-toolkit --exclude results --exclude util/k8s app Dockerfile requirements.txt
kubectl exec -it "$exec_pod_name" -n atlassian -- mkdir /dc-app-performance-toolkit
cat dcapt.tar.gz | kubectl exec -i -n atlassian "$exec_pod_name" -- tar xzf - -C /dc-app-performance-toolkit
rm -rf dcapt.tar.gz
end=$(date +%s)
runtime=$((end-start))
echo "INFO: Copy finished in $runtime seconds"

if [[ $2 == "--docker_image_rebuild" ]]; then
  echo "INFO: Rebuild docker image"
  kubectl exec -it "$exec_pod_name" -n atlassian -- docker build -t $DCAPT_DOCKER_IMAGE dc-app-performance-toolkit
fi

echo "INFO: Run bzt on the exec env pod"
kubectl exec -it "$exec_pod_name" -n atlassian -- docker run --shm-size=4g -v "/dc-app-performance-toolkit:/dc-app-performance-toolkit" $DCAPT_DOCKER_IMAGE "$1"
sleep 10

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