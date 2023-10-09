# This file configures the Terraform for Atlassian DC on Kubernetes for Data Center applications performance testing
# with DCAPT toolkit and "small" dataset.
# WARNING: this configuration deploys low capacity cluster with "small" dataset and does not suite for full scale
# performance results generation.
# Please configure this file carefully before installing the infrastructure.
# See https://developer.atlassian.com/platform/marketplace/dc-apps-performance-and-scale-testing/ for more information.

################################################################################
# Common Settings
################################################################################

# Unique name of your small-scale test cluster.
# This value can not be altered after the configuration has been applied.
# ! REQUIRED !
environment_name = "dcapt-product-small"

# Supported products: jira, confluence and bitbucket
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
resource_tags = {Name: "dcapt-testing-small"}

# Instance types that is preferred for EKS node group.
# Confluence, Jira  - use default value
# Bitbucket - ["t3.2xlarge"]
# ! REQUIRED !
instance_types     = ["t3.xlarge"]
instance_disk_size = 100

# Minimum and maximum size of the EKS cluster.
# Cluster-autoscaler is installed in the EKS cluster that will manage the requested capacity
# and increase/decrease the number of nodes accordingly. This ensures there is always enough resources for the workloads
# and removes the need to change this value.
min_cluster_capacity = 1
max_cluster_capacity = 1

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
# Please make sure valid confluence license is used without spaces and new line symbols.
# ! REQUIRED !
jira_license = "jira-license"

# Number of Jira/JSM application nodes
# Note: For initial installation this value needs to be set to 1 and it can be changed only after Jira is fully
# installed and configured.
jira_replica_count = 1

# Supported versions by DCAPT: https://github.com/atlassian/dc-app-performance-toolkit#supported-versions
#
# Jira version
jira_version_tag = "9.4.8"
# JSM version
# jira_version_tag = "5.4.8"

# Shared home restore configuration.
# Make sure Jira/JSM version set in `jira_version_tag` match the snapshot version.
#
# Jira 9.4.8 DCAPT small dataset EBS snapshot
 jira_shared_home_snapshot_id = "snap-0005a8c3cc297b294"
# Jira 8.20.24 DCAPT small dataset EBS snapshot
# jira_shared_home_snapshot_id = "snap-0c3cb60ddc50c1136"
# JSM 5.4.8 DCAPT small dataset EBS snapshot
# jira_shared_home_snapshot_id = "snap-02f299ef7f1f524b2"
# JSM 4.20.24 DCAPT small dataset EBS snapshot
# jira_shared_home_snapshot_id = "snap-0971e128b8d1d2af9"

# Database restore configuration.
# Make sure Jira/JSM version set in `jira_version_tag` match the snapshot version.
# Build number stored within the snapshot and Jira license are also required, so that Jira can be fully setup prior to start.
#
# Jira 9.4.8 DCAPT small dataset RDS snapshot
 jira_db_snapshot_id = "arn:aws:rds:us-east-2:585036043680:snapshot:dcapt-jira-small-9-4-8"
# Jira 8.20.24 DCAPT small dataset RDS snapshot
# jira_db_snapshot_id = "arn:aws:rds:us-east-2:585036043680:snapshot:dcapt-jira-small-8-20-24"
# JSM 5.4.8 DCAPT small dataset RDS snapshot
# jira_db_snapshot_id = "arn:aws:rds:us-east-2:585036043680:snapshot:dcapt-jsm-small-5-4-8"
# JSM 4.20.24 DCAPT small dataset RDS snapshot
# jira_db_snapshot_id = "arn:aws:rds:us-east-2:585036043680:snapshot:dcapt-jsm-small-4-20-24"

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
jira_local_home_size  = "10Gi"
jira_shared_home_size = "10Gi"

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

################################################################################
# Confluence Settings
################################################################################

# Confluence license
# To avoid storing license in a plain text file, we recommend storing it in an environment variable prefixed with `TF_VAR_` (i.e. `TF_VAR_confluence_license`) and keep the below line commented out
# If storing license as plain-text is not a concern for this environment, feel free to uncomment the following line and supply the license here.
# Please make sure valid confluence license is used without spaces and new line symbols.
# ! REQUIRED !
confluence_license = "confluence-license"

# Number of Confluence application nodes
# Note: For initial installation this value needs to be set to 1 and it can be changed only after Confluence is fully
# installed and configured.
confluence_replica_count = 1

# Supported versions by DCAPT: https://github.com/atlassian/dc-app-performance-toolkit#supported-versions
confluence_version_tag = "7.19.11"

# Shared home restore configuration.
# 8.1.4 DCAPT small dataset EBS snapshot
# confluence_shared_home_snapshot_id = "snap-0815ada397b953b93"
# 7.19.11 DCAPT small dataset EBS snapshot
confluence_shared_home_snapshot_id = "snap-00ede7dca448a6243"
# 7.13.18 DCAPT small dataset EBS snapshot
# confluence_shared_home_snapshot_id = "snap-055811dae848f13ae"

# Database restore configuration.
# Build number stored within the snapshot and Confluence license are also required, so that Confluence can be fully setup prior to start.
# 8.1.4 DCAPT small dataset RDS snapshot
# confluence_db_snapshot_id = "arn:aws:rds:us-east-2:585036043680:snapshot:dcapt-confluence-small-8-1-4"
# 7.19.11 DCAPT small dataset RDS snapshot
confluence_db_snapshot_id = "arn:aws:rds:us-east-2:585036043680:snapshot:dcapt-confluence-small-7-19-11"
# 7.13.18 DCAPT small dataset RDS snapshot
# confluence_db_snapshot_id = "arn:aws:rds:us-east-2:585036043680:snapshot:dcapt-confluence-small-7-13-18"

# Build number for a specific Confluence version can be found in the link below:
# https://developer.atlassian.com/server/confluence/confluence-build-information
# 8.1.4
# confluence_db_snapshot_build_number = "9003"
# 7.19.11
confluence_db_snapshot_build_number = "8804"
# 7.13.18
# confluence_db_snapshot_build_number = "8703"

# Helm chart version of Confluence
#confluence_helm_chart_version = "<helm_chart_version>"

# Installation timeout
# Different variables can influence how long it takes the application from installation to ready state. These
# can be dataset restoration, resource requirements, number of replicas and others.
confluence_installation_timeout = 20

# Confluence instance resource configuration
confluence_cpu      = "900m"
confluence_mem      = "6Gi"
confluence_min_heap = "2048m"
confluence_max_heap = "2048m"

# Synchrony instance resource configuration
synchrony_cpu       = "1"
synchrony_mem       = "2.5Gi"
synchrony_min_heap  = "1024m"
synchrony_max_heap  = "2048m"
synchrony_stack_size = "2048k"

# Storage
confluence_local_home_size  = "20Gi"
confluence_shared_home_size = "10Gi"

# Confluence NFS instance resource configuration
confluence_nfs_requests_cpu    = "500m"
confluence_nfs_requests_memory = "1Gi"
confluence_nfs_limits_cpu      = "500m"
confluence_nfs_limits_memory   = "2Gi"

# RDS instance configurable attributes. Note that the allowed value of allocated storage and iops may vary based on instance type.
# You may want to adjust these values according to your needs.
# Documentation can be found via:
# https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html
# https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Storage.html#USER_PIOPS
confluence_db_major_engine_version = "14"
confluence_db_instance_class       = "db.t3.medium"
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

# Custom values file location. Defaults to an empty string which means only values from config.tfvars
# are passed to Helm chart. Variables from config.tfvars take precedence over those defined in a custom values.yaml.
# confluence_custom_values_file = "/path/to/values.yaml"

################################################################################
# Bitbucket Settings
################################################################################

# Bitbucket license
# To avoid storing license in a plain text file, we recommend storing it in an environment variable prefixed with `TF_VAR_` (i.e. `TF_VAR_bitbucket_license`) and keep the below line commented out
# If storing license as plain-text is not a concern for this environment, feel free to uncomment the following line and supply the license here
# Please make sure valid bitbucket license is used without spaces and new line symbols.
# ! REQUIRED !
bitbucket_license = "bitbucket-license"

# Number of Bitbucket application nodes
# Note: For initial installation this value needs to be set to 1 and it can be changed only after Bitbucket is fully
# installed and configured.
bitbucket_replica_count = 1

# Supported versions by DCAPT: https://github.com/atlassian/dc-app-performance-toolkit#supported-versions
bitbucket_version_tag = "7.21.14"

# Shared home restore configuration.
# Make sure Bitbucket version set in `bitbucket_version_tag` match the snapshot version.
#
# 7.21.14 DCAPT small dataset EBS snapshot
bitbucket_shared_home_snapshot_id = "snap-03893c494ba7edcf4"
# 8.9.2 DCAPT small dataset EBS snapshot
#bitbucket_shared_home_snapshot_id = "snap-0fb8cd6bf387057c0"

# Database restore configuration.
# Make sure Bitbucket version set in `bitbucket_version_tag` match the snapshot version.
#
# 7.21.14 DCAPT small dataset RDS snapshot
bitbucket_db_snapshot_id = "arn:aws:rds:us-east-2:585036043680:snapshot:dcapt-bitbucket-small-7-21-14"
# 8.9.2 DCAPT small dataset RDS snapshot
#bitbucket_db_snapshot_id = "arn:aws:rds:us-east-2:585036043680:snapshot:dcapt-bitbucket-small-8-9-2"

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

# The display name of Bitbucket instance
#bitbucket_display_name = "<DISPLAY_NAME>"

# Bitbucket instance resource configuration
bitbucket_cpu      = "2"
bitbucket_mem      = "8Gi"
bitbucket_min_heap = "1024m"
bitbucket_max_heap = "2048m"

# Storage
bitbucket_local_home_size  = "10Gi"
bitbucket_shared_home_size = "20Gi"

# Bitbucket NFS instance resource configuration
bitbucket_nfs_requests_cpu    = "1"
bitbucket_nfs_requests_memory = "4Gi"
bitbucket_nfs_limits_cpu      = "1.5"
bitbucket_nfs_limits_memory   = "6Gi"

# Elasticsearch resource configuration for Bitbucket
bitbucket_elasticsearch_requests_cpu    = "1"
bitbucket_elasticsearch_requests_memory = "4Gi"
bitbucket_elasticsearch_limits_cpu      = "1.5"
bitbucket_elasticsearch_limits_memory   = "6Gi"
bitbucket_elasticsearch_storage         = "100"
bitbucket_elasticsearch_replicas        = "2"

# RDS instance configurable attributes. Note that the allowed value of allocated storage and iops may vary based on instance type.
# You may want to adjust these values according to your needs.
# Documentation can be found via:
# https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html
# https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Storage.html#USER_PIOPS
bitbucket_db_major_engine_version = "14"
bitbucket_db_instance_class       = "db.t3.medium"
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

# Custom values file location. Defaults to an empty string which means only values from config.tfvars
# are passed to Helm chart. Variables from config.tfvars take precedence over those defined in a custom values.yaml.
# bitbucket_custom_values_file = "/path/to/values.yaml"
