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

# Parse arguments for --ci flag (starting from 2nd argument)
ci=false
for ((i=2; i<=$#; i++)); do
  if [[ "${!i}" == "--ci" ]]; then
    ci=true
    break
  fi
done

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

# Ensure tmux is installed in the pod (using apk for Alpine)
echo "INFO: Ensuring tmux is available in the pod"
kubectl exec -i "$exec_pod_name" -n atlassian -- sh -c "command -v tmux || apk add --no-cache tmux"

# Check if tmux session already exists and contains our setup
session_exists=$(kubectl exec "$exec_pod_name" -n atlassian -- sh -c "tmux has-session -t bzt_session 2>/dev/null; echo \$?")

if [[ "$session_exists" == "0" ]]; then
  echo "INFO: Found existing tmux session 'bzt_session', attaching to it..."
else
  echo "INFO: Creating new tmux session and running setup inside it"
  
  # Prepare the dcapt archive locally first
  echo "INFO: Preparing dc-app-performance-toolkit archive"
  start=$(date +%s)
  tar -czf dcapt.tar.gz -C dc-app-performance-toolkit --exclude results --exclude util/k8s app Dockerfile requirements.txt
  
  # Copy the archive to the pod
  echo "INFO: Copying archive to pod"
  kubectl cp dcapt.tar.gz atlassian/"$exec_pod_name":/tmp/dcapt.tar.gz
  rm -rf dcapt.tar.gz
  end=$(date +%s)
  runtime=$((end-start))
  echo "INFO: Archive preparation and copy finished in $runtime seconds"
  
  # Create the setup script that will run inside tmux
  setup_script="
    echo 'INFO: Starting setup inside tmux session'
    
    # Cleanup and recreate directory
    echo 'INFO: Cleanup dc-app-performance-toolkit folder'
    rm -rf /dc-app-performance-toolkit
    mkdir -p /dc-app-performance-toolkit
    
    # Extract the archive
    echo 'INFO: Extracting dc-app-performance-toolkit'
    tar xzf /tmp/dcapt.tar.gz -C /dc-app-performance-toolkit
    rm -f /tmp/dcapt.tar.gz
    
    # Docker image rebuild if requested
    if [ '$2' = '--docker_image_rebuild' ]; then
      echo 'INFO: Rebuilding docker image'
      docker build -t $DCAPT_DOCKER_IMAGE dc-app-performance-toolkit
    fi
    
    # Create a marker file to indicate setup is complete
    touch /tmp/dcapt_setup_complete
    
    echo 'INFO: Setup complete, starting bzt execution'
    # Run bzt
    docker run --shm-size=4g -v /dc-app-performance-toolkit:/dc-app-performance-toolkit $DCAPT_DOCKER_IMAGE '$1'
  "
  
  # Start tmux session with the complete setup and execution
  kubectl exec -i "$exec_pod_name" -n atlassian -- sh -c "
    rm -f /tmp/bzt_session.log
    tmux new-session -d -s bzt_session \"$setup_script\"
    tmux pipe-pane -t bzt_session \"cat > /tmp/bzt_session.log\"
  "
  
  echo "INFO: Tmux session 'bzt_session' created with setup and execution"
fi

attempt=1
max_attempts=5
echo "INFO: Attaching to tmux session 'bzt_session'..."

while [ $attempt -le $max_attempts ]; do
  echo "INFO: Attempt $attempt to attach to tmux session 'bzt_session'..."
  
  # Check if session still exists before attempting to attach
  session_check=$(kubectl exec "$exec_pod_name" -n atlassian -- sh -c "tmux has-session -t bzt_session 2>/dev/null; echo \$?" 2>/dev/null)
  
  if [[ "$session_check" != "0" ]]; then
    echo "INFO: bzt session has finished or does not exist."
    break
  fi
  
  # Different behavior based on ci flag
  if [[ "$ci" == "true" ]]; then
    # CI mode: stream logs from /tmp/bzt_session.log (non-interactive)
    kubectl exec "$exec_pod_name" -n atlassian -- sh -c "
      tail -f /tmp/bzt_session.log &
      tail_pid=\$!
      
      while true; do
        sleep 5
        if ! tmux has-session -t bzt_session 2>/dev/null; then
          break
        fi
      done

      kill \$tail_pid 2>/dev/null || true
    " 2>/dev/null
    exit_code=$?
  else
    # Interactive mode: attach to tmux session
    kubectl exec -it "$exec_pod_name" -n atlassian -- tmux attach-session -t bzt_session 2>/dev/null
    exit_code=$?
  fi
  
  # Handle different exit scenarios
  if [[ $exit_code -eq 0 ]]; then
    echo "INFO: Successfully detached from tmux session."
    # Double-check if session still exists after clean detachment
    session_exists=$(kubectl exec "$exec_pod_name" -n atlassian -- sh -c "tmux has-session -t bzt_session 2>/dev/null; echo \$?" 2>/dev/null)
    if [[ "$session_exists" != "0" ]]; then
      echo "INFO: bzt session has completed."
      break
    fi
    # Clean detachment but session still exists, continue monitoring
    echo "INFO: Session still active, continuing to monitor..."
  elif [[ $exit_code -ne 0 ]]; then
    # Handle network errors or other failures
    echo "WARNING: Connection lost (exit code: $exit_code)"
    
    # Verify session still exists before retrying
    session_exists=$(kubectl exec "$exec_pod_name" -n atlassian -- sh -c "tmux has-session -t bzt_session 2>/dev/null; echo \$?" 2>/dev/null)
    
    if [[ "$session_exists" != "0" ]]; then
      echo "INFO: bzt session has finished during disconnection."
      break
    fi
    
    if [ $attempt -eq $max_attempts ]; then
      echo "ERROR: Reached maximum number of attempts ($max_attempts). Session may still be running."
      echo "ERROR: You can manually reconnect using: kubectl exec -it $exec_pod_name -n atlassian -- tmux attach-session -t bzt_session"
      break
    fi
    
    # Exponential backoff for retries
    sleep_time=$((2 + attempt))
    echo "INFO: Network error or disconnect detected, reconnecting to tmux session in $sleep_time seconds (attempt $((attempt+1)))..."
    sleep $sleep_time
    attempt=$((attempt+1))
  fi
done

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