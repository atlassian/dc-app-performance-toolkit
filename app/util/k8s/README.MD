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
-it atlassianlabs/terraform ./install.sh -c conf.tfvars
```
## Terminate development environment
``` bash
docker run --pull=always --env-file aws_envs \
-v "/$PWD/dcapt-small.tfvars:/data-center-terraform/conf.tfvars" \
-v "/$PWD/logs:/data-center-terraform/logs" \
-it atlassianlabs/terraform ./uninstall.sh -c conf.tfvars
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
-it atlassianlabs/terraform ./install.sh -c conf.tfvars
```
## Terminate enterprise-scale environment
Option `-t` deletes Terraform state files for all installed environment in the same region using the same AWS account.

If state files are needed, e.g. there are other running clusters for other product, do not use `-t` flag in below command.
``` bash
docker run --pull=always --env-file aws_envs \
-v "/$PWD/dcapt.tfvars:/data-center-terraform/conf.tfvars" \
-v "/$PWD/logs:/data-center-terraform/logs" \
-it atlassianlabs/terraform ./uninstall.sh -t -c conf.tfvars
```

# Collect detailed k8s logs
Set AWS credential in [aws_envs](./aws_envs) file and run command:
``` bash
export ENVIRONMENT_NAME=your_environment_name
export REGION=us-east-2

docker run --pull=always --env-file aws_envs \
-v "/$PWD/k8s_logs:/data-center-terraform/k8s_logs" \
-v "/$PWD/logs:/data-center-terraform/logs" \
-it atlassianlabs/terraform ./scripts/collect_k8s_logs.sh atlas-$ENVIRONMENT_NAME-cluster $REGION k8s_logs
```

# Force terminate cluster
Set AWS credential in [aws_envs](./aws_envs) file and run command:
``` bash
export ENVIRONMENT_NAME=your_environment_name
export REGION=us-east-2

docker run --pull=always --env-file aws_envs \
--workdir="/data-center-terraform" \
--entrypoint="python" \
-v "/$PWD/terminate_cluster.py:/data-center-terraform/terminate_cluster.py" \
atlassian/dcapt terminate_cluster.py --cluster_name atlas-$ENVIRONMENT_NAME-cluster --aws_region $REGION
```