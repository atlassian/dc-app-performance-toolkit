# Table of content:
- [Development environment](#development-environment)
  - [Create development environment](#create-development-environment)
  - [Terminate development environment](#terminate-development-environment)
- [Enterprise-scale environment](#enterprise-scale-environment)
  - [Create enterprise-scale environment](#create-enterprise-scale-environment)
  - [Terminate enterprise-scale environment](#terminate-enterprise-scale-environment)
- [Collect detailed k8s logs](#collect-detailed-k8s-logs)
- [Force terminate cluster](#force-terminate-cluster)
- [Connect to a product pod](#connect-to-a-product-pod)
- [Connect to the execution environment pod](#connect-to-the-execution-environment-pod)
- [Connect to the RDS database](#connect-to-the-rds-database)
- [Enable detailed resources monitoring](#enable-detailed-resources-monitoring)
- [Rebuild atlassian/dcapt docker image on the fly](#rebuild-atlassiandcapt-docker-image-on-the-fly)
- [Run tests locally from docker container](#run-tests-locally-from-docker-container)
- [Run tests from execution environment pod](#run-tests-from-execution-environment-pod)

# Development environment

### Create development environment
1. Navigate to `dc-app-performance-toolkit/app/util/k8s` folder
2. Set AWS credential in [aws_envs](./aws_envs) file
3. set correct values in [dcapt-small.tfvars](./dcapt-small.tfvars) file:
   * `environment_name`
   * `products`
   * `license`
4. Run install development environment command from :
``` bash
docker run --pull=always --env-file aws_envs \
-v "/$PWD/dcapt-small.tfvars:/data-center-terraform/conf.tfvars" \
-v "/$PWD/dcapt-snapshots.json:/data-center-terraform/dcapt-snapshots.json" \
-v "/$PWD/logs:/data-center-terraform/logs" \
-it atlassianlabs/terraform:2.7.7 ./install.sh -c conf.tfvars
```
### Terminate development environment
Note: install and uninstall commands have to use the same `atlassianlabs/terraform:TAG` image tag.
1. Navigate to `dc-app-performance-toolkit/app/util/k8s` folder
2. Set AWS credential in [aws_envs](./aws_envs) file
3. Run command:
``` bash
docker run --pull=always --env-file aws_envs \
-v "/$PWD/dcapt-small.tfvars:/data-center-terraform/conf.tfvars" \
-v "/$PWD/dcapt-snapshots.json:/data-center-terraform/dcapt-snapshots.json" \
-v "/$PWD/logs:/data-center-terraform/logs" \
-it atlassianlabs/terraform:2.7.7 ./uninstall.sh -c conf.tfvars
```

# Enterprise-scale environment
### Create enterprise-scale environment
1. Navigate to `dc-app-performance-toolkit/app/util/k8s` folder
2. Set AWS credential in [aws_envs](./aws_envs) file
3. Set correct values in [dcapt.tfvars](./dcapt.tfvars) file:
   * `environment_name`
   * `products`
   * `license`
4. Run install enterprise-scale environment command:
``` bash
docker run --pull=always --env-file aws_envs \
-v "/$PWD/dcapt.tfvars:/data-center-terraform/conf.tfvars" \
-v "/$PWD/dcapt-snapshots.json:/data-center-terraform/dcapt-snapshots.json" \
-v "/$PWD/logs:/data-center-terraform/logs" \
-it atlassianlabs/terraform:2.7.7 ./install.sh -c conf.tfvars
```
### Terminate enterprise-scale environment
Note: install and uninstall commands have to use the same `atlassianlabs/terraform:TAG` image tag.
1. Navigate to `dc-app-performance-toolkit/app/util/k8s` folder
2. Set AWS credential in [aws_envs](./aws_envs) file
3. Run command:
``` bash
docker run --pull=always --env-file aws_envs \
-v "/$PWD/dcapt.tfvars:/data-center-terraform/conf.tfvars" \
-v "/$PWD/dcapt-snapshots.json:/data-center-terraform/dcapt-snapshots.json" \
-v "/$PWD/logs:/data-center-terraform/logs" \
-it atlassianlabs/terraform:2.7.7 ./uninstall.sh -c conf.tfvars
```

# Collect detailed k8s logs
Note: On unsuccessful deployment detailed logs generated automatically
in `dc-app-performance-toolkit/app/util/logs/k8s_logs` folder.

To generate detailed k8s logs:
1. Navigate to `dc-app-performance-toolkit/app/util/k8s` folder
2. Set AWS credential in [aws_envs](./aws_envs) file
3. Run command:
``` bash
export ENVIRONMENT_NAME=your_environment_name
export REGION=us-east-2
```

``` bash
docker run --pull=always --env-file aws_envs \
-v "/$PWD/k8s_logs:/data-center-terraform/k8s_logs" \
-v "/$PWD/logs:/data-center-terraform/logs" \
-it atlassianlabs/terraform:2.7.7 ./scripts/collect_k8s_logs.sh atlas-$ENVIRONMENT_NAME-cluster $REGION k8s_logs
```

# Force terminate cluster
1. Navigate to `dc-app-performance-toolkit/app/util/k8s` folder
2. Set AWS credential in [aws_envs](./aws_envs) file
3. Run command:
``` bash
export ENVIRONMENT_NAME=your_environment_name
export REGION=us-east-2
```

``` bash
docker run --pull=always --env-file aws_envs \
--workdir="//data-center-terraform" \
--entrypoint="python" \
-v "/$PWD/terminate_cluster.py:/data-center-terraform/terminate_cluster.py" \
atlassian/dcapt terminate_cluster.py --cluster_name atlas-$ENVIRONMENT_NAME-cluster --aws_region $REGION
```

# Connect to a product pod
1. Navigate to `dc-app-performance-toolkit/app/util/k8s` folder
2. Set AWS credential in [aws_envs](./aws_envs) file
3. Set your environment name:
    ``` bash
    export ENVIRONMENT_NAME=your_environment_name
    export REGION=us-east-2
    ```
4. SSH to terraform container:
    ``` bash
    docker run --pull=always --env-file aws_envs \
    -e ENVIRONMENT_NAME=$ENVIRONMENT_NAME \
    -e REGION=$REGION \
    -it atlassianlabs/terraform:2.7.7 bash 
    ```

5. Connect to the product pod. Example below for jira pod with number 0. For other product or pod number change `PRODUCT_POD` accordingly.
    ``` bash
    export PRODUCT_POD=jira-0
    aws eks update-kubeconfig --name atlas-$ENVIRONMENT_NAME-cluster --region $REGION
    kubectl exec -it $PRODUCT_POD -n atlassian -- bash
    ```

# Connect to the execution environment pod
1. Navigate to `dc-app-performance-toolkit` folder
2. Set AWS credential in [aws_envs](./aws_envs) file
3. Set your environment name:
    ``` bash
    export ENVIRONMENT_NAME=your_environment_name
    export REGION=us-east-2
    ```
4. SSH to terraform container:
    ``` bash
    docker run --pull=always --env-file ./app/util/k8s/aws_envs \
    -e ENVIRONMENT_NAME=$ENVIRONMENT_NAME \
    -e REGION=$REGION \
    -v "/$PWD:/data-center-terraform/dc-app-performance-toolkit" \
    -it atlassianlabs/terraform:2.7.7 bash 
    ```
5. Copy code base and connect to the execution environment pod:
    ``` bash
    aws eks update-kubeconfig --name atlas-$ENVIRONMENT_NAME-cluster --region $REGION
    exec_pod_name=$(kubectl get pods -n atlassian -l=exec=true --no-headers -o custom-columns=":metadata.name")
    kubectl exec -it "$exec_pod_name" -n atlassian -- rm -rf /dc-app-performance-toolkit
    kubectl cp --retries 10 dc-app-performance-toolkit atlassian/"$exec_pod_name":/dc-app-performance-toolkit
    kubectl exec -it "$exec_pod_name" -n atlassian -- bash
    ```

# Connect to the RDS database
1. Navigate to `dc-app-performance-toolkit/app/util/k8s` folder
2. Set AWS credential in [aws_envs](./aws_envs) file
3. Export environment variables for environment name, region and product:
    ``` bash
    export ENVIRONMENT_NAME=your_environment_name
    export REGION=us-east-2
    export PRODUCT=jira
    # PRODUCT options: jira/confluence/bitbucket. For jsm use jira as well.
    ```
4. Start and ssh to `atlassianlabs/terraform` docker container:
    ``` bash
    docker run --pull=always --env-file aws_envs \
    -e ENVIRONMENT_NAME=$ENVIRONMENT_NAME \
    -e REGION=$REGION \
    -e PRODUCT=$PRODUCT \
    -v "/$PWD/script-runner.yml:/data-center-terraform/script-runner.yml" \
    -it atlassianlabs/terraform:2.7.7 bash 
    ```
5. Run following commands one by one inside docker container:
    ``` bash
    aws eks update-kubeconfig --name atlas-$ENVIRONMENT_NAME-cluster --region $REGION
    kubectl apply -f script-runner.yml
    rds_endpoint=$(aws rds --region $REGION describe-db-instances --filters "Name=db-instance-id,Values=atlas-${ENVIRONMENT_NAME}-${PRODUCT}-db" --query "DBInstances[].Endpoint.Address" --output text)
    kubectl exec -it script-runner -- psql -h $rds_endpoint -d $PRODUCT -U atl$PRODUCT
    ```
6. Default DB password: `Password1!`

# Enable detailed resources monitoring
To enable detailed CPU/Memory monitoring and Grafana dashboards for visualisation:
1. Navigate to `dc-app-performance-toolkit/app/util/k8s` folder
2. Set AWS credential in [aws_envs](./aws_envs) file
3. Go to `dcapt.tvars` file -> Monitoring section
4. Uncomment and set to `true` following required variables: `monitoring_enabled` and `monitoring_grafana_expose_lb`
5. Modify if needed other optional variables
6. Do `install.sh` as described in [Create enterprise-scale environment](#create-enterprise-scale-environment)
7. Get Grafana URL:
    ``` bash
    export ENVIRONMENT_NAME=your_environment_name
    export REGION=us-east-2
    ```
    ``` bash
    docker run --pull=always --env-file aws_envs \
    -e ENVIRONMENT_NAME=$ENVIRONMENT_NAME \
    -e REGION=$REGION \
    -it atlassianlabs/terraform:2.7.7 bash 
    ```
    ``` bash
    aws eks update-kubeconfig --name atlas-$ENVIRONMENT_NAME-cluster --region $REGION
    kubectl get svc -n kube-monitoring | grep grafana
    ```
8. Open Grafana URL in the browser. Default Grafana creds: `admin/prom-operator`.
9. Go to Dashboards -> General -> select one of the available dashboards.

# Rebuild atlassian/dcapt docker image on the fly
In case any changes are needed in `atlassian/dcapt` image:
1. Modify locally `dc-app-performance-toolkit/Dockerfile` file
2. [Run tests from execution environment pod](#run-tests-from-execution-environment-pod) with extra flag in the end `--docker_image_rebuild`

# Run tests locally from docker container
Note: this option is **not** suitable for full-scale performance runs as local network is a bottleneck.
1. Navigate to `dc-app-performance-toolkit` folder
2. Select needed product and run below command (example below is for jira):
    ``` bash
    docker run --pull=always --shm-size=4g -v "/$PWD:/dc-app-performance-toolkit" atlassian/dcapt jira.yml
    ```
   
# Run tests from execution environment pod
1. Navigate to `dc-app-performance-toolkit` folder
2. Set AWS credential in [aws_envs](./aws_envs) file
3. Set environment name:
    ``` bash
    export ENVIRONMENT_NAME=your_environment_name
    ```
4. Select needed product and run below command (example below is for jira):
    ``` bash
    docker run --pull=always --env-file ./app/util/k8s/aws_envs \
    -e REGION=us-east-2 \
    -e ENVIRONMENT_NAME=$ENVIRONMENT_NAME \
    -v "/$PWD:/data-center-terraform/dc-app-performance-toolkit" \
    -v "/$PWD/app/util/k8s/bzt_on_pod.sh:/data-center-terraform/bzt_on_pod.sh" \
    -it atlassianlabs/terraform:2.7.7 bash bzt_on_pod.sh jira.yml
    ```
