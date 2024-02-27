# Development environment

## Create development environment 
* set AWS credential in [aws_envs](./aws_envs) file
* set correct values in [dcapt-small.tfvars](./dcapt-small.tfvars) file:
  * `environment_name`
  * `products`
  * `license`
* run install development environment command:
``` bash
docker run --pull=always --env-file aws_envs \
-v "/$PWD/dcapt-small.tfvars:/data-center-terraform/conf.tfvars" \
-v "/$PWD/dcapt-snapshots.json:/data-center-terraform/dcapt-snapshots.json" \
-v "/$PWD/logs:/data-center-terraform/logs" \
-it atlassianlabs/terraform:2.7.1 ./install.sh -c conf.tfvars
```
## Terminate development environment
Note: install and uninstall commands have to use the same `atlassianlabs/terraform:TAG` image tag.
Set AWS credential in [aws_envs](./aws_envs) file and run command:
``` bash
docker run --pull=always --env-file aws_envs \
-v "/$PWD/dcapt-small.tfvars:/data-center-terraform/conf.tfvars" \
-v "/$PWD/dcapt-snapshots.json:/data-center-terraform/dcapt-snapshots.json" \
-v "/$PWD/logs:/data-center-terraform/logs" \
-it atlassianlabs/terraform:2.7.1 ./uninstall.sh -c conf.tfvars
```

# Enterprise-scale environment
## Create enterprise-scale environment
* set AWS credential in [aws_envs](./aws_envs) file
* set correct values in [dcapt.tfvars](./dcapt.tfvars) file:
  * `environment_name`
  * `products`
  * `license`
* run install enterprise-scale environment command:
``` bash
docker run --pull=always --env-file aws_envs \
-v "/$PWD/dcapt.tfvars:/data-center-terraform/conf.tfvars" \
-v "/$PWD/dcapt-snapshots.json:/data-center-terraform/dcapt-snapshots.json" \
-v "/$PWD/logs:/data-center-terraform/logs" \
-it atlassianlabs/terraform:2.7.1 ./install.sh -c conf.tfvars
```
## Terminate enterprise-scale environment
Note: install and uninstall commands have to use the same `atlassianlabs/terraform:TAG` image tag.
Set AWS credential in [aws_envs](./aws_envs) file and run command:
``` bash
docker run --pull=always --env-file aws_envs \
-v "/$PWD/dcapt.tfvars:/data-center-terraform/conf.tfvars" \
-v "/$PWD/dcapt-snapshots.json:/data-center-terraform/dcapt-snapshots.json" \
-v "/$PWD/logs:/data-center-terraform/logs" \
-it atlassianlabs/terraform:2.7.1 ./uninstall.sh -c conf.tfvars
```

# Collect detailed k8s logs
Set AWS credential in [aws_envs](./aws_envs) file and run command:
``` bash
export ENVIRONMENT_NAME=your_environment_name
export REGION=us-east-2
```

``` bash
docker run --pull=always --env-file aws_envs \
-v "/$PWD/k8s_logs:/data-center-terraform/k8s_logs" \
-v "/$PWD/logs:/data-center-terraform/logs" \
-it atlassianlabs/terraform:2.7.1 ./scripts/collect_k8s_logs.sh atlas-$ENVIRONMENT_NAME-cluster $REGION k8s_logs
```

# Force terminate cluster
Set AWS credential in [aws_envs](./aws_envs) file and run command:
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

# Connect to product pod
Set your environment name:
``` bash
export ENVIRONMENT_NAME=your_environment_name
export REGION=us-east-2
```

SSH to terraform container:
``` bash
docker run --pull=always --env-file aws_envs \
-e ENVIRONMENT_NAME=$ENVIRONMENT_NAME \
-e REGION=$REGION \
-it atlassianlabs/terraform:2.7.1 bash 
```

Connect to the product pod. Example below for jira pod with number 0. For other product or pod number change `PRODUCT_POD` accordingly.
``` bash
export PRODUCT_POD=jira-0
aws eks update-kubeconfig --name atlas-$ENVIRONMENT_NAME-cluster --region $REGION
kubectl exec -it $PRODUCT_POD -n atlassian -- bash
```

# Enable detailed resources monitoring
To enable detailed CPU/Memory monitoring and Grafana dashboards for visualisation:
1. Go to `dcapt.tvars` file -> Monitoring section.
2. Uncomment and set to `true` following required variables: `monitoring_enabled` and `monitoring_grafana_expose_lb`.
3. Modify if needed other optional variables.
4. Do `install.sh` as described in [Create enterprise-scale environment](#create-enterprise-scale-environment).
5. Get Grafana URL:
    ``` bash
    export ENVIRONMENT_NAME=your_environment_name
    export REGION=us-east-2
    ```
    ``` bash
    docker run --pull=always --env-file aws_envs \
    -e ENVIRONMENT_NAME=$ENVIRONMENT_NAME \
    -e REGION=$REGION \
    -it atlassianlabs/terraform:2.7.1 bash 
    ```
    ``` bash
    aws eks update-kubeconfig --name atlas-$ENVIRONMENT_NAME-cluster --region $REGION
    kubectl get svc -n kube-monitoring | grep grafana
    ```
6. Open Grafana URL in the browser. Default Grafana creds: `admin/prom-operator`.
7. Go to Dashboards -> General -> select one of the available dashboards.

# Connect to RDS database
1. Set AWS credential in [aws_envs](./aws_envs) file
2. Export environment variables for environment name, region and product:
    ``` bash
    export ENVIRONMENT_NAME=your_environment_name
    export REGION=us-east-2
    export PRODUCT=jira
    # PRODUCT options: jira/jsm/confluence/bitbucket/crowd/bamboo
    ```
3. Start and ssh to `atlassianlabs/terraform` docker container:
    ``` bash
    docker run --pull=always --env-file aws_envs \
    -e ENVIRONMENT_NAME=$ENVIRONMENT_NAME \
    -e REGION=$REGION \
    -e PRODUCT=$PRODUCT \
    -v "/$PWD/script-runner.yml:/data-center-terraform/script-runner.yml" \
    -it atlassianlabs/terraform:2.7.1 bash 
    ```
4. Run following command one by one inside docker container:
    ``` bash
    aws eks update-kubeconfig --name atlas-$ENVIRONMENT_NAME-cluster --region $REGION
    kubectl apply -f script-runner.yml
    rds_endpoint=$(aws rds --region $REGION describe-db-instances --filters "Name=db-instance-id,Values=atlas-${ENVIRONMENT_NAME}-${PRODUCT}-db" --query "DBInstances[].Endpoint.Address" --output text)
    kubectl exec -it script-runner -- psql -h $rds_endpoint -d $PRODUCT -U atl$PRODUCT
    ```
5. Default DB password: `Password1!`

# Run tests locally from docker container
1. Navigate to `dc-app-performance-toolkit` folder
2. Select needed product and run below command (example below is for jira):
    ``` bash
    docker run --pull=always --shm-size=4g -v "/$PWD:/dc-app-performance-toolkit" atlassian/dcapt jira.yml
    ```
   
# Run tests from execution environment pod
1. Navigate to `dc-app-performance-toolkit` folder
2. Set environment name:
    ``` bash
    export ENVIRONMENT_NAME=your_environment_name
    ```
3. Select needed product and run below command (example below is for jira):
    ``` bash
    docker run --pull=always --env-file ./app/util/k8s/aws_envs \
    -e REGION=us-east-2 \
    -e ENVIRONMENT_NAME=$ENVIRONMENT_NAME \
    -v "/$PWD:/data-center-terraform/dc-app-performance-toolkit" \
    -v "/$PWD/app/util/k8s/bzt_on_pod.sh:/data-center-terraform/bzt_on_pod.sh" \
    -it atlassianlabs/terraform:2.7.1 bash bzt_on_pod.sh jira.yml
    ```
