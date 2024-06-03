# This file configures the Terraform for Atlassian DC on Kubernetes for Data Center applications performance testing
# with DCAPT toolkit and "small" dataset.
# WARNING: this configuration deploys low capacity cluster with "small" dataset and does not suite for full scale
# performance results generation.
# Please configure this file carefully before installing the infrastructure.
# See https://developer.atlassian.com/platform/marketplace/dc-apps-performance-and-scale-testing/ for more information.

################################################################################
# Configuration settings to change
################################################################################

# Unique name of your small-scale test cluster.
# This value can not be altered after the configuration has been applied.
# ! REQUIRED !
environment_name = "dcapt-product-small"

# Supported products: jira, confluence and bitbucket.
# For JSM set product as jira.
# e.g.: products = ["jira"]
# ! REQUIRED !
products = ["jira"]

# License
# To avoid storing license in a plain text file, we recommend storing it in an environment variable prefixed with `TF_VAR_` (i.e. `TF_VAR_jira_license`) and keep the below line commented out
# If storing license as plain-text is not a concern for this environment, feel free to uncomment the following line and supply the license here.
# ! IMPORTANT ! Please make sure valid license is used without spaces and new line symbols.
# ! REQUIRED !
jira_license = "AAAB4A0ODAoPeNqVUl1v2jAUfc+viLSXTigoUJq2SJFWEq+wJqEQKK3Ey224gEeII9tJl/36OgkINjqqPfrYvueejy8+S3QfCt20dLPTvbrtmte64070ttnuaA5HkJQlLki0S8QwrwzT0jwaYSJwUqQYwBZtZ+j7ZOwM7jztJ+XQ3N2TBS1/2ySYkPHjeBASLci2r8iHy6lALmyjtR9FfqWUF0c8lqKqh6WcLbJINsuDIdhSvgHHJkSS5mhLnqEWZq8i4jStyCqE5BBncDhXg9R0cDCRyGswrqn7INa277w533vZjHuLvt95es4l9FvWZgbMJR2n17hbj+R9J/B+p7Miyp8L12os70eNULBoOV3N7bm9VzJwbW/ghiQwPKXEur1pndURSuDlRkuIhVKCPEeuRvRmLw/GaBrMjBdnODGG5tjXNlg8KddKUS3LNK/Nm8vLlrbiiMmapSnyM74/Zjxag8C/kzz+XVmTcir2tpLA/lPHB1wfdcDFQxw/lFo93KnVL8oM9DqEr/OufshJ84EqNIEk+v8ynLTqeNHjppyZ8Y927B1va0O+goSKulUqNMq2EONGQLLgLKcR/bbaAo2bEdtqDkuk4iVKVPzZ22qnEwUVerL6GdN3lBX8CeM7t3Ff7zAsAhQrn/MTehde1w+uZciB8aTYJzpykAIUfvLWETNs6qNSYiCHyd0jANFkBfI=X02mq"

# (Optional) Domain name used by the ingress controller.
# The final ingress domain is a subdomain within this domain. (eg.: environment.domain.com)
# You can also provide a subdomain <subdomain.domain.com> and the final ingress domain will be <environment.subdomain.domain.com>.
# When commented out, the ingress controller is not provisioned and the application is accessible over HTTP protocol (not HTTPS).
#
#domain = "<example.com>"

################################################################################
# Common Settings
################################################################################

# Default AWS region for DCAPT snapshots. Supported regions: us-east-2, us-east-1.
# If any other specific region is required, please contact support via community slack channel.
region = "us-east-2"

# List of IP ranges that are allowed to access the running applications over the World Wide Web.
# By default the deployed applications are publicly accessible (0.0.0.0/0). You can restrict this access by changing the
# default value to your desired CIDR blocks. e.g. ["10.20.0.0/16" , "99.68.64.0/10"]
whitelist_cidr = ["0.0.0.0/0"]

# Path to a JSON file with EBS and RDS snapshot IDs
snapshots_json_file_path = "dcapt-snapshots.json"

# (optional) Custom tags for all resources to be created. Please add all tags you need to propagate among the resources.
resource_tags = {Name: "dcapt-testing-small"}

# Instance types that is preferred for EKS node group.
instance_types     = ["t3.xlarge"]
instance_disk_size = 100

# Minimum and maximum size of the EKS cluster.
# Cluster-autoscaler is installed in the EKS cluster that will manage the requested capacity
# and increase/decrease the number of nodes accordingly. This ensures there is always enough resources for the workloads
# and removes the need to change this value.
min_cluster_capacity = 1
max_cluster_capacity = 4

# By default, Ingress controller listens on 443 and 80. You can enable only http port 80 by
# uncommenting the below line, which will disable port 443. This results in fewer inbound rules in Nginx controller security group.
# This can be used in case you hit the limit which can happen if 30+ whitelist_cidrs are provided.
#enable_https_ingress = false

################################################################################
# Jira/JSM Settings
################################################################################

# To select a different image repository for the Jira application, you can change following variable:
# Official suitable values are:
# - "atlassian/jira-software"
# - "atlassian/jira-servicemanagement"
#
# Jira
jira_image_repository = "atlassian/jira-software"
# JSM
# ! REQUIRED for JSM !
# jira_image_repository = "atlassian/jira-servicemanagement"

# Supported versions by DCAPT: https://github.com/atlassian/dc-app-performance-toolkit#supported-versions
# Jira version.
jira_version_tag = "9.12.4"
# JSM version
# ! REQUIRED for JSM !
# jira_version_tag = "5.12.4"

# Dataset size. Used only when snapshots_json_file_path is defined. Defaults to large
jira_dataset_size = "small"

# Number of Jira/JSM application nodes
# Note: For initial installation this value needs to be set to 1 and it can be changed only after Jira is fully
# installed and configured.
jira_replica_count = 1

# Helm chart version of Jira
# jira_helm_chart_version = "<helm_chart_version>"

# Installation timeout
# Different variables can influence how long it takes the application from installation to ready state. These
# can be dataset restoration, resource requirements, number of replicas and others.
jira_installation_timeout = 20

# Jira/JSM instance resource configuration
jira_cpu                 = "1500m"
jira_mem                 = "11Gi"
jira_min_heap            = "4096m"
jira_max_heap            = "4096m"
jira_reserved_code_cache = "2048m"

# Jira/JSM NFS instance resource configuration
jira_nfs_requests_cpu    = "500m"
jira_nfs_requests_memory = "1Gi"
jira_nfs_limits_cpu      = "1"
jira_nfs_limits_memory   = "1.5Gi"

# Storage
# initial volume size of local/shared home EBS.
jira_local_home_size  = "20Gi"
jira_shared_home_size = "20Gi"

# RDS instance configurable attributes. Note that the allowed value of allocated storage and iops may vary based on instance type.
# You may want to adjust these values according to your needs.
# Documentation can be found via:
# https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html
# https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Storage.html#USER_PIOPS
jira_db_major_engine_version = "12"
jira_db_instance_class       = "db.t3.medium"
jira_db_allocated_storage    = 200
jira_db_iops                 = 1000

# If you restore the database, make sure `jira_db_name' is set to the db name from the snapshot.
# Set `null` if the snapshot does not have a default db name.
jira_db_name = "jira"

# The master user credential for the database instance.
# If username is not provided, it'll be default to "postgres".
# If password is not provided, a random password will be generated.
jira_db_master_username = "atljira"
jira_db_master_password = "Password1!"

# Custom values file location. Defaults to an empty string which means only values from config.tfvars
# are passed to Helm chart. Variables from config.tfvars take precedence over those defined in a custom values.yaml.
# jira_custom_values_file = "/path/to/values.yaml"

# A list of JVM arguments to be passed to the server. Defaults to an empty list.
# Example: ["-Dproperty=value", "-Dproperty1=value1"]
jira_additional_jvm_args = ["-Dupm.plugin.upload.enabled=true"]