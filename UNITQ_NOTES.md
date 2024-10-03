# Overview

To run this you must add valid admin credentials to `app/jira.yml`

See https://developer.atlassian.com/platform/marketplace/dc-apps-performance-and-scale-testing/ for what to do with this repo. You can skip to Step 5 titled `Enterprise-scale Environment`

Please check the version of the terraform container and the current available Jira LTS's before beginning testing.

## Installation 

Use the unitq-sandbox account. There is a hosted zone in R53 called `jiratest.unitq.us`. If this does not exist, a hosted zone must be setup for the installation script to create the records required for a secure connection. 

An IAM user with full admin access must be created in the account and the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` added to `app/util/k8s/aws_envs`

Run the following to setup Jira DC from `app/util/k8s`, you can add the path to aws_envs if you wish to run this from the base of the repo:

```sh

docker run --platform linux/amd64 --pull=always --env-file aws_envs \
 -v "/Users/ntowne/repos/atlassian/dc-app-performance-toolkit/app/util/k8s/dcapt.tfvars:/data-center-terraform/conf.tfvars" \
 -v "/Users/ntowne/repos/atlassian/dc-app-performance-toolkit/app/util/k8s/dcapt-snapshots.json:/data-center-terraform/dcapt-snapshots.json" \
 -v "/Users/ntowne/repos/atlassian/dc-app-performance-toolkit/app/util/k8s/logs:/data-center-terraform/logs" \
 -it atlassianlabs/terraform:2.9.2 ./install.sh -c conf.tfvars

```

This will take about 30-45 minutes to setup.

For scaling testing, run the above script but change the value of `jira_replica_count` in `dcapt.tfvars` as required.

## Testing

For each step of testing run the following, changing the absolute paths as required:

```sh

 docker run --platform linux/amd64 --pull=always --env-file aws_envs \
 -e REGION=us-east-2 \
-e ENVIRONMENT_NAME="unitq-jira-testing" \
-v "/Users/ntowne/repos/atlassian/dc-app-performance-toolkit:/data-center-terraform/dc-app-performance-toolkit" \
-v "/Users/ntowne/repos/atlassian/dc-app-performance-toolkit/app/util/k8s/bzt_on_pod.sh:/data-center-terraform/bzt_on_pod.sh" \
-it atlassianlabs/terraform:2.9.2 bash bzt_on_pod.sh jira.yml

```

Update the `jira.yml` file as needed. For the first two runs app specific actions should be disabled.

After Run 1 of Step 8 our Jira app must be installed. See instructions [here](https://docs.google.com/document/d/188wLOuTHduoCjFQUFN6srxRV2sQRKDbcx2mjEl0wAqU/edit#heading=h.8sx1wi5oltrp). The jar files are stored in [Artifactory](https://unitq.jfrog.io/ui/native/libs-release-local/com/unitq/jira-server-plugin/)

Before running scalability testing, create at least 5 tickets in Jira with the summary field containing `Appissue`, such as `Appissue 1, Appissue 2, etc`. Once these tickets are created, add them to the unitQ Jira plugin in unitQ Monitor, this can be done by searching for the issue name or via a direct link. 

### Accessing Kubernetes

If needed, you can access EKS directly from your workstation. Use the credentials in `aws_envs` to become the user used to install Jira. This user has full access to the EKS cluster. Run the following to update your kubeconfig:

```bash

aws eks update-kubeconfig --name atlas-unitq-jira-testing-cluster --region us-east-2

```

You should now be able to access the EKS cluster containing the Jira pods.