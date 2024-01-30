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