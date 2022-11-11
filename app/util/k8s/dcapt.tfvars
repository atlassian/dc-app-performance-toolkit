# This file configures the Terraform for Atlassian DC on Kubernetes.
# Please configure this file carefully before installing the infrastructure.
# See https://atlassian-labs.github.io/data-center-terraform/userguide/CONFIGURATION/ for more information.

################################################################################
# Common Settings
################################################################################

# 'environment_name' provides your environment a unique name within a single cloud provider account.
# This value can not be altered after the configuration has been applied.
environment_name = "dcapt-product"

# Cloud provider region that this configuration will deploy to.
region = "us-east-2"

# (optional) List of the products to be installed.
# Supported products are confluence and bamboo.
# e.g.: products = ["confluence"]
products = ["product-to-deploy"]

# List of IP ranges that are allowed to access the running applications over the World Wide Web.
# By default the deployed applications are publicly accessible (0.0.0.0/0). You can restrict this access by changing the
# default value to your desired CIDR blocks. e.g. ["10.20.0.0/16" , "99.68.64.0/10"]
whitelist_cidr = ["0.0.0.0/0"]

# (Optional) Domain name used by the ingress controller.
# The final ingress domain is a subdomain within this domain. (eg.: environment.domain.com)
# You can also provide a subdomain <subdomain.domain.com> and the final ingress domain will be <environment.subdomain.domain.com>.
# When commented out, the ingress controller is not provisioned and the application is accessible over HTTP protocol (not HTTPS).
#
#domain = "<example.com>"

# (optional) Custom tags for all resources to be created. Please add all tags you need to propagate among the resources.
resource_tags = {Name: "dcapt-testing"}

# Instance types that is preferred for EKS node group.
instance_types     = ["m5.2xlarge"]
instance_disk_size = 100

# Minimum and maximum size of the EKS cluster.
# Cluster-autoscaler is installed in the EKS cluster that will manage the requested capacity
# and increase/decrease the number of nodes accordingly. This ensures there is always enough resources for the workloads
# and removes the need to change this value.
min_cluster_capacity = 1
max_cluster_capacity = 4

################################################################################
# Jira Settings
################################################################################

# Helm chart version of Jira
jira_helm_chart_version = "1.5.0"

# Number of Jira application nodes
# Note: For initial installation this value needs to be set to 1 and it can be changed only after Jira is fully
# installed and configured.
jira_replica_count = 1

# Installation timeout
# Different variables can influence how long it takes the application from installation to ready state. These
# can be dataset restoration, resource requirements, number of replicas and others.
jira_installation_timeout = 20

# Termination grace period
# Under certain conditions, pods may be stuck in a Terminating state which forces shared-home pvc to be stuck
# in Terminating too causing Terraform destroy error (timing out waiting for a deleted PVC).
# Termination grace period is 0 by default. You can override it if for some reason you need a different value
jira_termination_grace_period = 0

# By default, Jira Software will use the version defined in the Helm chart. If you wish to override the version, uncomment
# the following line and set the jira_version_tag to any of the versions available on https://hub.docker.com/r/atlassian/jira-software/tags
jira_version_tag = "jira-version"

# To select a different image repository for the Jira application, you can change following variable:
# Official suitable values are:
# - "atlassian/jira-software"
# - "atlassian/jira-servicemanagement"
jira_image_repository = "atlassian/jira-software"

# Jira instance resource configuration
jira_cpu                 = "7"
jira_mem                 = "28Gi"
jira_min_heap            = "12288m"
jira_max_heap            = "12288m"
jira_reserved_code_cache = "512m"

# Jira NFS instance resource configuration
#jira_nfs_requests_cpu    = "<REQUESTS_CPU>"
#jira_nfs_requests_memory = "<REQUESTS_MEMORY>"
#jira_nfs_limits_cpu      = "<LIMITS_CPU>"
#jira_nfs_limits_memory   = "<LIMITS_MEMORY>"

# Shared home restore configuration
# To restore a shared home dataset, you can provide an EBS snapshot ID that contains the content of the shared home volume.
# This volume will be mounted to the NFS server and used when the product is started.
# Make sure the snapshot is available in the region you are deploying to and it follows all product requirements.
jira_shared_home_snapshot_id = "snap-0b41108b0741d726a"

# Storage
# initial volume size of local/shared home EBS.
jira_local_home_size  = "200Gi"
jira_shared_home_size = "200Gi"

# RDS instance configurable attributes. Note that the allowed value of allocated storage and iops may vary based on instance type.
# You may want to adjust these values according to your needs.
# Documentation can be found via:
# https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html
# https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Storage.html#USER_PIOPS
jira_db_major_engine_version = "11"
jira_db_instance_class       = "db.m5.xlarge"
jira_db_allocated_storage    = 200
jira_db_iops                 = 1000
# If you restore the database, make sure `jira_db_name' is set to the db name from the snapshot.
# Set `null` if the snapshot does not have a default db name.
jira_db_name = "jira"

# Database restore configuration
# If you want to restore the database from a snapshot, uncomment the following line and provide the snapshot identifier.
# This will restore the database from the snapshot and will not create a new database.
# The snapshot should be in the same AWS account and region as the environment to be deployed.
# You must provide Jira license if you wish to retore the database from a snapshot.
# You must provide jira_db_master_username and jira_db_master_password that matches the ones in snapshot
jira_db_snapshot_id = "jira-large-k8s"
jira_license = "jira-license"

# The master user credential for the database instance.
# If username is not provided, it'll be default to "postgres".
# If password is not provided, a random password will be generated.
jira_db_master_username     = "postgres"
jira_db_master_password     = "Password1!"

################################################################################
# Confluence Settings
################################################################################

# Helm chart version of Confluence
confluence_helm_chart_version = "1.5.1"

# Number of Confluence application nodes
# Note: For initial installation this value needs to be set to 1 and it can be changed only after Confluence is fully
# installed and configured.
confluence_replica_count = 1

# Installation timeout
# Different variables can influence how long it takes the application from installation to ready state. These
# can be dataset restoration, resource requirements, number of replicas and others.
confluence_installation_timeout = 25

# Termination grace period
# Under certain conditions, pods may be stuck in a Terminating state which forces shared-home pvc to be stuck
# in Terminating too causing Terraform destroy error (timing out waiting for a deleted PVC).
# Termination grace period is 0 by default. You can override it if for some reason you need a different value
confluence_termination_grace_period = 0

# By default, Confluence will use the version defined in the Helm chart. If you wish to override the version, uncomment
# the following line and set the confluence_version_tag to any of the versions available on https://hub.docker.com/r/atlassian/confluence/tags
confluence_version_tag = "7.19.2"

# Confluence license
# To avoid storing license in a plain text file, we recommend storing it in an environment variable prefixed with `TF_VAR_` (i.e. `TF_VAR_confluence_license`) and keep the below line commented out
# If storing license as plain-text is not a concern for this environment, feel free to uncomment the following line and supply the license here
#
confluence_license = "confluence-license"

# Confluence instance resource configuration
confluence_cpu      = "4"
confluence_mem      = "20Gi"
confluence_min_heap = "12288m"
confluence_max_heap = "12288m"

# Synchrony instance resource configuration
synchrony_cpu       = "2"
synchrony_mem       = "2.5Gi"
synchrony_min_heap  = "1024m"
synchrony_max_heap  = "2048m"
synchrony_stack_size = "2048k"

# Storage
confluence_local_home_size  = "200Gi"
confluence_shared_home_size = "100Gi"

# Confluence NFS instance resource configuration
#confluence_nfs_requests_cpu    = "<REQUESTS_CPU>"
#confluence_nfs_requests_memory = "<REQUESTS_MEMORY>"
#confluence_nfs_limits_cpu      = "<LIMITS_CPU>"
#confluence_nfs_limits_memory   = "<LIMITS_MEMORY>"

# Shared home restore configuration
# To restore shared home dataset, you can provide EBS snapshot ID of the shared home volume.
# This volume will be mounted to the NFS server and used when the product is started.
# Make sure the snapshot is available in the region you are deploying to and it follows all product requirements.
# 7.19.2
confluence_shared_home_snapshot_id = "snap-0b0101e17d318658e"
# 7.13.7
# confluence_shared_home_snapshot_id = "snap-0f89356e59f45801f"

# RDS instance configurable attributes. Note that the allowed value of allocated storage and iops may vary based on instance type.
# You may want to adjust these values according to your needs.
# Documentation can be found via:
# https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html
# https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Storage.html#USER_PIOPS
confluence_db_major_engine_version = "11"
confluence_db_instance_class       = "db.m5.xlarge"
confluence_db_allocated_storage    = 200
confluence_db_iops                 = 1000
# If you restore the database, make sure `confluence_db_name' is set to the db name from the snapshot.
# Set `null` if the snapshot does not have a default db name.
confluence_db_name = "confluence"

# Database restore configuration
# If you want to restore the database from a snapshot, uncomment the following lines and provide the snapshot identifier.
# This will restore the database from the snapshot and will not create a new database.
# The snapshot should be in the same AWS account and region as the environment to be deployed.
# Please also provide confluence_db_master_username and confluence_db_master_password that matches the ones in snapshot
# Build number stored within the snapshot and Confluence license are also required, so that Confluence can be fully setup prior to start.
# 7.19.2
confluence_db_snapshot_id = "confluence-719-large-k8s-psql11"
# 7.13.7
# confluence_db_snapshot_id = "confluence-large-k8s-psql11"

# Build number for a specific Confluence version can be found in the link below:
# https://developer.atlassian.com/server/confluence/confluence-build-information
# 7.19.2
confluence_db_snapshot_build_number = "8804"
# 7.13.7
# confluence_db_snapshot_build_number = "8703"

# The master user credential for the database instance.
# If username is not provided, it'll be default to "postgres".
# If password is not provided, a random password will be generated.
confluence_db_master_username = "atlconfluence"
confluence_db_master_password = "Password1!"

# Enables Collaborative editing in Confluence
confluence_collaborative_editing_enabled = true

################################################################################
# Bitbucket Settings
################################################################################

# Helm chart version of Bitbucket
bitbucket_helm_chart_version = "1.5.0"

# Number of Bitbucket application nodes
bitbucket_replica_count = 1

# Installation timeout
# Different variables can influence how long it takes the application from installation to ready state. These
# can be dataset restoration, resource requirements, number of replicas and others.
bitbucket_installation_timeout = 20

# Termination grace period
# Under certain conditions, pods may be stuck in a Terminating state which forces shared-home pvc to be stuck
# in Terminating too causing Terraform destroy error (timing out waiting for a deleted PVC).
# Termination grace period is 0 by default. You can override it if for some reason you need a different value
bitbucket_termination_grace_period = 0

# By default, Bitbucket will use the version defined in the Bitbucket Helm chart:
# https://github.com/atlassian/data-center-helm-charts/blob/main/src/main/charts/bitbucket/Chart.yaml
# If you wish to override the version, uncomment the following line and set the bitbucket_version_tag to any of the versions published for Bitbucket on Docker Hub: https://hub.docker.com/r/atlassian/bitbucket/tags
bitbucket_version_tag = "bitbucket-version"

# Bitbucket license
# To avoid storing license in a plain text file, we recommend storing it in an environment variable prefixed with `TF_VAR_` (i.e. `TF_VAR_bitbucket_license`) and keep the below line commented out
# If storing license as plain-text is not a concern for this environment, feel free to uncomment the following line and supply the license here
#
bitbucket_license = "bitbucket-license"

# Bitbucket system admin credentials
# To pre-seed Bitbucket with the system admin information, uncomment the following settings and supply the system admin information:
#
# To avoid storing password in a plain text file, we recommend storing it in an environment variable prefixed with `TF_VAR_`
# (i.e. `TF_VAR_bitbucket_admin_password`) and keep `bitbucket_admin_password` commented out
# If storing password as plain-text is not a concern for this environment, feel free to uncomment `bitbucket_admin_password` and supply system admin password here
#
bitbucket_admin_username      = "admin"
bitbucket_admin_password      = "admin"
bitbucket_admin_display_name  = "admin"
bitbucket_admin_email_address = "admin@example.com"

# The display name of Bitbucket instance
#bitbucket_display_name = "<DISPLAY_NAME>"

# Bitbucket instance resource configuration
bitbucket_cpu      = "6"
bitbucket_mem      = "20Gi"
bitbucket_min_heap = "256m"
bitbucket_max_heap = "512m"

# Storage
bitbucket_local_home_size  = "1500Gi"
bitbucket_shared_home_size = "1500Gi"

# RDS instance configurable attributes. Note that the allowed value of allocated storage and iops may vary based on instance type.
# You may want to adjust these values according to your needs.
# Documentation can be found via:
# https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html
# https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Storage.html#USER_PIOPS
bitbucket_db_major_engine_version = "11"
bitbucket_db_instance_class       = "db.m5.xlarge"
bitbucket_db_allocated_storage    = 200
bitbucket_db_iops                 = 1000
# If you restore the database, make sure `bitbucket_db_name' is set to the db name from the snapshot.
# Set `null` if the snapshot does not have a default db name.
bitbucket_db_name = "bitbucket"

# Bitbucket NFS instance resource configuration
bitbucket_nfs_requests_cpu    = "4"
bitbucket_nfs_requests_memory = "16Gi"
bitbucket_nfs_limits_cpu      = "4.5"
bitbucket_nfs_limits_memory   = "17Gi"

# Elasticsearch resource configuration for Bitbucket
bitbucket_elasticsearch_requests_cpu    = "2"
bitbucket_elasticsearch_requests_memory = "8Gi"
bitbucket_elasticsearch_limits_cpu      = "2.5"
bitbucket_elasticsearch_limits_memory   = "9Gi"
bitbucket_elasticsearch_storage         = "500"
bitbucket_elasticsearch_replicas        = "2"

# Dataset Restore

# Database restore configuration
# If you want to restore the database from a snapshot, uncomment the following line and provide the snapshot identifier.
# This will restore the database from the snapshot and will not create a new database.
# The snapshot should be in the same AWS account and region as the environment to be deployed.
# Please also provide bitbucket_db_master_username and bitbucket_db_master_password that matches the ones in snapshot
bitbucket_db_snapshot_id = "bitbucket-large-k8s"

# The master user credential for the database instance.
# If username is not provided, it'll be default to "postgres".
# If password is not provided, a random password will be generated.
bitbucket_db_master_username     = "postgres"
bitbucket_db_master_password     = "Password1!"

# Shared home restore configuration
# To restore shared home dataset, you can provide EBS snapshot ID that contains content of the shared home volume.
# This volume will be mounted to the NFS server and used when the product is started.
# Make sure the snapshot is available in the region you are deploying to and it follows all product requirements.
bitbucket_shared_home_snapshot_id = "snap-00161e6291871f63c"

################################################################################
# Bamboo Settings
################################################################################

# Helm chart version of Bamboo and Bamboo agent instances
bamboo_helm_chart_version       = "1.5.0"
bamboo_agent_helm_chart_version = "1.5.0"

# By default, Bamboo and the Bamboo Agent will use the versions defined in their respective Helm charts:
# https://github.com/atlassian/data-center-helm-charts/blob/main/src/main/charts/bamboo/Chart.yaml
# https://github.com/atlassian/data-center-helm-charts/blob/main/src/main/charts/bamboo-agent/Chart.yaml
# If you wish to override these versions, uncomment the following lines and set the bamboo_version_tag and bamboo_agent_version_tag to any of the versions published on Docker Hub:
# https://hub.docker.com/r/atlassian/bamboo/tags
# https://hub.docker.com/r/atlassian/bamboo-agent-base/tags
bamboo_version_tag       = "bamboo-version"
bamboo_agent_version_tag = "bamboo-version"

# Bamboo license
# To avoid storing license in a plain text file, we recommend storing it in an environment variable prefixed with `TF_VAR_` (i.e. `TF_VAR_bamboo_license`) and keep the below line commented out
# If storing license as plain-text is not a concern for this environment, feel free to uncomment the following line and supply the license here
#
bamboo_license = "bamboo-license"

# Bamboo system admin credentials
# To pre-seed Bamboo with the system admin information, uncomment the following settings and supply the system admin information:
#
# WARNING: In case you are restoring an existing dataset (see the `dataset_url` property below), you will need to use credentials
# existing in the dataset to set this section. Otherwise any other value for the `bamboo_admin_*` properties below are ignored.
#
# To avoid storing password in a plain text file, we recommend storing it in an environment variable prefixed with `TF_VAR_`
# (i.e. `TF_VAR_bamboo_admin_password`) and keep `bamboo_admin_password` commented out
# If storing password as plain-text is not a concern for this environment, feel free to uncomment `bamboo_admin_password` and supply system admin password here
#
bamboo_admin_username      = "admin"
bamboo_admin_password      = "admin"
bamboo_admin_display_name  = "admin"
bamboo_admin_email_address = "admin@example.com"

# Installation timeout
# Different variables can influence how long it takes the application from installation to ready state. These
# can be dataset restoration, resource requirements, number of replicas and others.
#bamboo_installation_timeout = <MINUTES>

# Bamboo instance resource configuration
bamboo_cpu      = "4"
bamboo_mem      = "16Gi"
bamboo_min_heap = "256m"
bamboo_max_heap = "512m"

# Bamboo Agent instance resource configuration
bamboo_agent_cpu = "200m"
bamboo_agent_mem = "700m"

# Storage
bamboo_local_home_size  = "200Gi"
bamboo_shared_home_size = "400Gi"

# Bamboo NFS instance resource configuration
#bamboo_nfs_requests_cpu    = "<REQUESTS_CPU>"
#bamboo_nfs_requests_memory = "<REQUESTS_MEMORY>"
#bamboo_nfs_limits_cpu      = "<LIMITS_CPU>"
#bamboo_nfs_limits_memory   = "<LIMITS_MEMORY>"

# Number of Bamboo remote agents to launch
# To install and use the Bamboo agents, you need to provide pre-seed data including a valid Bamboo license and system admin information.
number_of_bamboo_agents = 50

# RDS instance configurable attributes. Note that the allowed value of allocated storage and iops may vary based on instance type.
# You may want to adjust these values according to your needs.
# Documentation can be found via:
# https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html
# https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Storage.html#USER_PIOPS
bamboo_db_major_engine_version = "13"
bamboo_db_instance_class       = "db.t3.medium"
bamboo_db_allocated_storage    = 100
bamboo_db_iops                 = 1000
bamboo_db_name                 = "bamboo"

# (Optional) URL for dataset to import
# The provided default is the dataset used in the DCAPT framework.
# See https://developer.atlassian.com/platform/marketplace/dc-apps-performance-toolkit-user-guide-bamboo
#
bamboo_dataset_url = "https://centaurus-datasets.s3.amazonaws.com/bamboo/dcapt-bamboo.zip"

# Termination grace period
# Under certain conditions, pods may be stuck in a Terminating state which forces shared-home pvc to be stuck
# in Terminating too causing Terraform destroy error (timing out waiting for a deleted PVC).
# Termination grace period is 0 by default. You can override it if for some reason you need a different value.
# This will apply to both Bamboo server and agent pods.
bamboo_termination_grace_period = 0