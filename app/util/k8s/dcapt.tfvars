# This file configures the Terraform for Atlassian DC on Kubernetes for Data Center applications performance testing
# with DCAPT toolkit and enterprise-scale dataset.
# Please configure this file carefully before installing the infrastructure.
# See https://developer.atlassian.com/platform/marketplace/dc-apps-performance-and-scale-testing/ for more information.

################################################################################
# Common Settings
################################################################################

# Unique name of your enterprise-scale test cluster.
# This value can not be altered after the configuration has been applied.
# ! REQUIRED !
environment_name = "dcapt-product"

# Supported products: jira, confluence, bitbucket and bamboo.
# e.g.: products = ["confluence"]
# ! REQUIRED !
products = ["product-to-deploy"]

# Default AWS region for DCAPT snapshots.
region = "us-east-2"

# List of IP ranges that are allowed to access the running applications over the World Wide Web.
# By default the deployed applications are publicly accessible (0.0.0.0/0). You can restrict this access by changing the
# default value to your desired CIDR blocks. e.g. ["10.20.0.0/16" , "99.68.64.0/10"]
whitelist_cidr = ["0.0.0.0/0"]

# (optional) Custom tags for all resources to be created. Please add all tags you need to propagate among the resources.
resource_tags = {Name: "dcapt-testing"}

# Instance types that is preferred for EKS node group.
# Confluence, Bamboo, Jira - use default value
# Bitbucket - ["m5.4xlarge"]
# Crowd - ["c5.xlarge"]
# ! REQUIRED !
instance_types     = ["m5.2xlarge"]
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

# (Optional) Domain name used by the ingress controller.
# The final ingress domain is a subdomain within this domain. (eg.: environment.domain.com)
# You can also provide a subdomain <subdomain.domain.com> and the final ingress domain will be <environment.subdomain.domain.com>.
# When commented out, the ingress controller is not provisioned and the application is accessible over HTTP protocol (not HTTPS).
#
#domain = "<example.com>"

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
# jira_image_repository = "atlassian/jira-servicemanagement"

# Jira/JSM license
# To avoid storing license in a plain text file, we recommend storing it in an environment variable prefixed with `TF_VAR_` (i.e. `TF_VAR_jira_license`) and keep the below line commented out
# If storing license as plain-text is not a concern for this environment, feel free to uncomment the following line and supply the license here.
# Please make sure valid Jira/JSM license is used without spaces and new line symbols.
# ! REQUIRED !
jira_license = "jira-license"

# Number of Jira/JSM application nodes
# Note: For initial installation this value needs to be set to 1 and it can be changed only after Jira is fully
# installed and configured.
jira_replica_count = 1

# Supported versions by DCAPT: https://github.com/atlassian/dc-app-performance-toolkit#supported-versions
#
# Jira version
jira_version_tag = "9.4.6"
# JSM version
# jira_version_tag = "5.4.6"

# Shared home restore configuration.
# Make sure Jira/JSM version set in `jira_version_tag` match the snapshot version.
#
# Jira 9.4.6 DCAPT large dataset EBS snapshot
jira_shared_home_snapshot_id = "snap-051b68559232b9c52"
# Jira 8.20.22 DCAPT large dataset EBS snapshot
# jira_shared_home_snapshot_id = "snap-07eabc725b2784dd8"
# JSM 5.4.6 DCAPT large dataset EBS snapshot
# jira_shared_home_snapshot_id = "snap-0a65d52f20fc43d4e"
# JSM 4.20.22 DCAPT large dataset EBS snapshot
# jira_shared_home_snapshot_id = "snap-02cf7f70e3872320f"

# Database restore configuration.
# Make sure Jira/JSM version set in `jira_version_tag` match the snapshot version.
# Build number stored within the snapshot and Jira license are also required, so that Jira can be fully setup prior to start.
#
# Jira 9.4.6 DCAPT large dataset RDS snapshot
jira_db_snapshot_id = "arn:aws:rds:us-east-2:585036043680:snapshot:dcapt-jira-9-4-6"
# Jira 8.20.22 DCAPT large dataset RDS snapshot
# jira_db_snapshot_id = "arn:aws:rds:us-east-2:585036043680:snapshot:dcapt-jira-8-20-22"
# JSM 5.4.6 DCAPT large dataset RDS snapshot
# jira_db_snapshot_id = "arn:aws:rds:us-east-2:585036043680:snapshot:dcapt-jsm-5-4-6"
# JSM 4.20.22 DCAPT large dataset RDS snapshot
# jira_db_snapshot_id = "arn:aws:rds:us-east-2:585036043680:snapshot:dcapt-jsm-4-20-22"

# Helm chart version of Jira
# jira_helm_chart_version = "<helm_chart_version>"

# Installation timeout
# Different variables can influence how long it takes the application from installation to ready state. These
# can be dataset restoration, resource requirements, number of replicas and others.
jira_installation_timeout = 25

# Jira/JSM instance resource configuration
jira_cpu                 = "6"
jira_mem                 = "24Gi"
jira_min_heap            = "12288m"
jira_max_heap            = "12288m"
jira_reserved_code_cache = "2048m"

# Storage
# initial volume size of local/shared home EBS.
jira_local_home_size  = "100Gi"
jira_shared_home_size = "100Gi"

# RDS instance configurable attributes. Note that the allowed value of allocated storage and iops may vary based on instance type.
# You may want to adjust these values according to your needs.
# Documentation can be found via:
# https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html
# https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Storage.html#USER_PIOPS
jira_db_major_engine_version = "12"
jira_db_instance_class       = "db.m5.xlarge"
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

################################################################################
# Confluence Settings
################################################################################

# Confluence license
# To avoid storing license in a plain text file, we recommend storing it in an environment variable prefixed with `TF_VAR_` (i.e. `TF_VAR_confluence_license`) and keep the below line commented out
# If storing license as plain-text is not a concern for this environment, feel free to uncomment the following line and supply the license here.
# Please make sure valid Confluence license is used without spaces and new line symbols.
# ! REQUIRED !
confluence_license = "confluence-license"

# Number of Confluence application nodes
# Note: For initial installation this value needs to be set to 1 and it can be changed only after Confluence is fully
# installed and configured.
confluence_replica_count = 1

# Supported versions by DCAPT: https://github.com/atlassian/dc-app-performance-toolkit#supported-versions
confluence_version_tag = "7.19.9"

# Shared home restore configuration.
# Make sure confluence version set in `confluence_version_tag` match the snapshot version.
#
# 8.1.4 DCAPT large dataset EBS snapshot
# confluence_shared_home_snapshot_id = "snap-0125fdfcf37dabef5"
# 7.19.9 DCAPT large dataset EBS snapshot
confluence_shared_home_snapshot_id = "snap-0bd74575c95014c10"
# 7.13.17 DCAPT large dataset EBS snapshot
# confluence_shared_home_snapshot_id = "snap-08abae6cf1937e958"

# Database restore configuration.
# Make sure confluence version set in `confluence_version_tag` match the snapshot version.
# Build number stored within the snapshot and Confluence license are also required, so that Confluence can be fully setup prior to start.
#
# 8.1.4 DCAPT large dataset RDS snapshot
# confluence_db_snapshot_id = "arn:aws:rds:us-east-2:585036043680:snapshot:dcapt-confluence-8-1-4"
# 7.19.9 DCAPT large dataset RDS snapshot
confluence_db_snapshot_id = "arn:aws:rds:us-east-2:585036043680:snapshot:dcapt-confluence-7-19-9"
# 7.13.17 DCAPT large dataset RDS snapshot
# confluence_db_snapshot_id = "arn:aws:rds:us-east-2:585036043680:snapshot:dcapt-confluence-7-13-17"

# Build number for a specific Confluence version can be found in the link below:
# https://developer.atlassian.com/server/confluence/confluence-build-information
# 8.1.4
# confluence_db_snapshot_build_number = "9003"
# 7.19.9
confluence_db_snapshot_build_number = "8804"
# 7.13.17
# confluence_db_snapshot_build_number = "8703"

# Helm chart version of Confluence
# confluence_helm_chart_version = "<helm_chart_version>"

# Installation timeout
# Different variables can influence how long it takes the application from installation to ready state. These
# can be dataset restoration, resource requirements, number of replicas and others.
confluence_installation_timeout = 25

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

# RDS instance configurable attributes. Note that the allowed value of allocated storage and iops may vary based on instance type.
# You may want to adjust these values according to your needs.
# Documentation can be found via:
# https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html
# https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Storage.html#USER_PIOPS
confluence_db_major_engine_version = "14"
confluence_db_instance_class       = "db.m5.xlarge"
confluence_db_allocated_storage    = 200
confluence_db_iops                 = 1000
# If you restore the database, make sure `confluence_db_name' is set to the db name from the snapshot.
# Set `null` if the snapshot does not have a default db name.
confluence_db_name = "confluence"

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

# Bitbucket license
# To avoid storing license in a plain text file, we recommend storing it in an environment variable prefixed with `TF_VAR_` (i.e. `TF_VAR_bitbucket_license`) and keep the below line commented out
# If storing license as plain-text is not a concern for this environment, feel free to uncomment the following line and supply the license here
# Please make sure valid Bitbucket license is used without spaces and new line symbols.
# ! REQUIRED !
bitbucket_license = "bitbucket-license"

# Number of Bitbucket application nodes
# Note: For initial installation this value needs to be set to 1 and it can be changed only after Bitbucket is fully
# installed and configured.
bitbucket_replica_count = 1

# Supported versions by DCAPT: https://github.com/atlassian/dc-app-performance-toolkit#supported-versions
bitbucket_version_tag = "7.21.11"

# Shared home restore configuration.
# Make sure Bitbucket version set in `bitbucket_version_tag` match the snapshot version.
#
# 7.21.11 DCAPT large dataset EBS snapshot
bitbucket_shared_home_snapshot_id = "snap-0456406e413ff835b"
# 8.8.3 DCAPT large dataset EBS snapshot
#bitbucket_shared_home_snapshot_id = "snap-04138d264fb24f2e7"
# 7.17.16 DCAPT large dataset EBS snapshot
#bitbucket_shared_home_snapshot_id = "snap-06fceac7bdcc3844c"

# Database restore configuration.
# Make sure Bitbucket version set in `bitbucket_version_tag` match the snapshot version.
#
# 7.21.11 DCAPT large dataset RDS snapshot
bitbucket_db_snapshot_id = "arn:aws:rds:us-east-2:585036043680:snapshot:dcapt-bitbucket-7-21-11"
# 8.8.3 DCAPT large dataset RDS snapshot
#bitbucket_db_snapshot_id = "arn:aws:rds:us-east-2:585036043680:snapshot:dcapt-bitbucket-8-8-3"
# 7.17.16 DCAPT large dataset RDS snapshot
#bitbucket_db_snapshot_id = "arn:aws:rds:us-east-2:585036043680:snapshot:dcapt-bitbucket-7-17-16"

# Helm chart version of Bitbucket
#bitbucket_helm_chart_version = "<helm_chart_version>"

# Installation timeout
# Different variables can influence how long it takes the application from installation to ready state. These
# can be dataset restoration, resource requirements, number of replicas and others.
bitbucket_installation_timeout = 30

# Termination grace period
# Under certain conditions, pods may be stuck in a Terminating state which forces shared-home pvc to be stuck
# in Terminating too causing Terraform destroy error (timing out waiting for a deleted PVC). Set termination graceful period to 0
# if you encounter such an issue
bitbucket_termination_grace_period = 0

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

# Bitbucket instance resource configuration
bitbucket_cpu      = "4"
bitbucket_mem      = "16Gi"
bitbucket_min_heap = "2048m"
bitbucket_max_heap = "4096m"

# Storage
bitbucket_local_home_size  = "1000Gi"
bitbucket_shared_home_size = "1000Gi"

# Bitbucket NFS instance resource configuration
bitbucket_nfs_requests_cpu    = "2"
bitbucket_nfs_requests_memory = "8Gi"
bitbucket_nfs_limits_cpu      = "3"
bitbucket_nfs_limits_memory   = "10Gi"

# Elasticsearch resource configuration for Bitbucket
bitbucket_elasticsearch_requests_cpu    = "1.5"
bitbucket_elasticsearch_requests_memory = "4Gi"
bitbucket_elasticsearch_limits_cpu      = "2"
bitbucket_elasticsearch_limits_memory   = "5Gi"
bitbucket_elasticsearch_storage         = "1000"
bitbucket_elasticsearch_replicas        = "2"

# RDS instance configurable attributes. Note that the allowed value of allocated storage and iops may vary based on instance type.
# You may want to adjust these values according to your needs.
# Documentation can be found via:
# https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html
# https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Storage.html#USER_PIOPS
bitbucket_db_major_engine_version = "14"
bitbucket_db_instance_class       = "db.m5.large"
bitbucket_db_allocated_storage    = 100
bitbucket_db_iops                 = 1000
# If you restore the database, make sure `bitbucket_db_name' is set to the db name from the snapshot.
# Set `null` if the snapshot does not have a default db name.
bitbucket_db_name = "bitbucket"

# The master user credential for the database instance.
# If username is not provided, it'll be default to "postgres".
# If password is not provided, a random password will be generated.
bitbucket_db_master_username = "atlbitbucket"
bitbucket_db_master_password = "Password1!"

################################################################################
# Crowd Settings
################################################################################

# Crowd license
# To avoid storing license in a plain text file, we recommend storing it in an environment variable prefixed with `TF_VAR_` (i.e. `TF_VAR_crowd_license`) and keep the below line commented out
# If storing license as plain-text is not a concern for this environment, feel free to uncomment the following line and supply the license here
# Please make sure valid Crowd license is used without spaces and new line symbols.
# ! REQUIRED !
crowd_license = "crowd-license"

# Number of Crowd application nodes
# Note: For initial installation this value needs to be set to 1 and it can be changed only after Crowd is fully
# installed and configured.
crowd_replica_count = 1

# Supported versions by DCAPT: https://github.com/atlassian/dc-app-performance-toolkit#supported-versions
crowd_version_tag = "5.0.5"

# Dataset Restore

# Shared home restore configuration
# To restore shared home dataset, you can provide EBS snapshot ID that contains content of the shared home volume.
# This volume will be mounted to the NFS server and used when the product is started.
# Make sure the snapshot is available in the region you are deploying to and it follows all product requirements.
#
# Crowd 5.0.5 DCAPT large dataset EBS snapshot
crowd_shared_home_snapshot_id = "snap-0da31ed523c51a0af"

# Database restore configuration
# If you want to restore the database from a snapshot, uncomment the following line and provide the snapshot identifier.
# This will restore the database from the snapshot and will not create a new database.
# The snapshot should be in the same AWS account and region as the environment to be deployed.
# Please also provide crowd_db_master_username and crowd_db_master_password that matches the ones in snapshot
#
# Crowd 5.0.2 DCAPT large dataset RDS snapshot
crowd_db_snapshot_id           = "arn:aws:rds:us-east-2:585036043680:snapshot:dcapt-crowd-5-0-5"
crowd_db_snapshot_build_number = "1794"

# Helm chart version of Crowd and Crowd agent instances. By default the latest version is installed.
# crowd_helm_chart_version       = "<helm_chart_version>"

# Installation timeout
# Different variables can influence how long it takes the application from installation to ready state. These
# can be dataset restoration, resource requirements, number of replicas and others.
crowd_installation_timeout = 20

# Crowd instance resource configuration
crowd_cpu      = "2"
crowd_mem      = "3Gi"
crowd_min_heap = "1024m"
crowd_max_heap = "1024m"

# Storage
crowd_local_home_size  = "10Gi"
crowd_shared_home_size = "10Gi"

# Crowd NFS instance resource configuration
crowd_nfs_requests_cpu    = "1"
crowd_nfs_requests_memory = "1Gi"
crowd_nfs_limits_cpu      = "1"
crowd_nfs_limits_memory   = "1Gi"

# RDS instance configurable attributes. Note that the allowed value of allocated storage and iops may vary based on instance type.
# You may want to adjust these values according to your needs.
# Documentation can be found via:
# https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html
# https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Storage.html#USER_PIOPS
crowd_db_major_engine_version = "14"
crowd_db_instance_class       = "db.m5.large"
crowd_db_allocated_storage    = 200
crowd_db_iops                 = 1000
crowd_db_name                 = "crowd"

# Termination grace period
# Under certain conditions, pods may be stuck in a Terminating state which forces shared-home pvc to be stuck
# in Terminating too causing Terraform destroy error (timing out waiting for a deleted PVC). Set termination graceful period to 0
# if you encounter such an issue. This will apply to Crowd pods.
crowd_termination_grace_period = 0

# The master user credential for the database instance.
# If username is not provided, it'll be default to "postgres".
# If password is not provided, a random password will be generated.
crowd_db_master_username     = "atlcrowd"
crowd_db_master_password     = "Password1!"

################################################################################
# Bamboo Settings
################################################################################

# Bamboo license
# To avoid storing license in a plain text file, we recommend storing it in an environment variable prefixed with `TF_VAR_` (i.e. `TF_VAR_bamboo_license`) and keep the below line commented out
# If storing license as plain-text is not a concern for this environment, feel free to uncomment the following line and supply the license here.
# Please make sure valid Bamboo license is used without spaces and new line symbols.
# ! REQUIRED !
bamboo_license = "bamboo-license"

# By default, latest supported by DCAPT version is set.
# https://hub.docker.com/r/atlassian/bamboo/tags
# https://hub.docker.com/r/atlassian/bamboo-agent-base/tags
bamboo_version_tag       = "9.2.1"
bamboo_agent_version_tag = "9.2.1"

# Helm chart version of Bamboo and Bamboo agent instances
# bamboo_helm_chart_version       = "<helm_chart_version>"
# bamboo_agent_helm_chart_version = "<helm_chart_version>"

# Number of Bamboo remote agents to launch
# To install and use the Bamboo agents, you need to provide pre-seed data including a valid Bamboo license and system admin information.
number_of_bamboo_agents = 50

# Termination grace period
# Under certain conditions, pods may be stuck in a Terminating state which forces shared-home pvc to be stuck
# in Terminating too causing Terraform destroy error (timing out waiting for a deleted PVC). Set termination graceful period to 0
# if you encounter such an issue
bamboo_termination_grace_period = 0

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
bamboo_installation_timeout = 20

# Bamboo instance resource configuration
bamboo_cpu      = "4"
bamboo_mem      = "16Gi"
bamboo_min_heap = "2048m"
bamboo_max_heap = "4096m"

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
