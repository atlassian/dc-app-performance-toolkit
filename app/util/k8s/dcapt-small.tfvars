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

# Supported products: confluence and bitbucket
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
# Confluence - use default value
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
confluence_version_tag = "7.19.2"

# Shared home restore configuration.
# 8.x.x
# confluence_shared_home_snapshot_id = "snap-0be9055e5b42333fd"
# 7.x.x
confluence_shared_home_snapshot_id = "snap-0237a9f4c1a332dc6"

# Database restore configuration.
# Build number stored within the snapshot and Confluence license are also required, so that Confluence can be fully setup prior to start.
# 8.x.x
# confluence_db_snapshot_id = "arn:aws:rds:us-east-2:585036043680:dcapt-confluence-small-8-0-x-psql14"
# 7.x.x
confluence_db_snapshot_id = "arn:aws:rds:us-east-2:585036043680:snapshot:dcapt-confluence-small-7-19-x-psql14"

# Build number for a specific Confluence version can be found in the link below:
# https://developer.atlassian.com/server/confluence/confluence-build-information
# 8.x.x
# confluence_db_snapshot_build_number = "9002"
# 7.x.x
confluence_db_snapshot_build_number = "8703"

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
confluence_db_master_username = "postgres"
confluence_db_master_password = "Password1!"

# Enables Collaborative editing in Confluence
confluence_collaborative_editing_enabled = true


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
bitbucket_version_tag = "7.21.7"

# Shared home restore configuration.
# Make sure Bitbucket version set in `bitbucket_version_tag` match the snapshot version.
#
# 7.21.7 DCAPT small dataset EBS snapshot
bitbucket_shared_home_snapshot_id = "snap-014e88755f53c2284"
# 8.0.5 DCAPT small dataset EBS snapshot
#bitbucket_shared_home_snapshot_id = "snap-04f8cce571e8ff53b"
# 7.17.13 DCAPT small dataset EBS snapshot
#bitbucket_shared_home_snapshot_id = "snap-0291604b41056ad4e"

# Database restore configuration.
# Make sure Bitbucket version set in `bitbucket_version_tag` match the snapshot version.
#
# 7.21.7 DCAPT small dataset RDS snapshot
 bitbucket_db_snapshot_id = "arn:aws:rds:us-east-2:585036043680:snapshot:dcapt-bitbucket-small-7-21-x"
# 8.0.5 DCAPT small dataset RDS snapshot
#bitbucket_db_snapshot_id = "arn:aws:rds:us-east-2:585036043680:snapshot:dcapt-bitbucket-small-8-0-x"
# 7.17.13 DCAPT small dataset RDS snapshot
#bitbucket_db_snapshot_id = "arn:aws:rds:us-east-2:585036043680:snapshot:dcapt-bitbucket-small-7-17-x"

# Helm chart version of Bitbucket
#bitbucket_helm_chart_version = "<helm_chart_version>"

# Installation timeout
# Different variables can influence how long it takes the application from installation to ready state. These
# can be dataset restoration, resource requirements, number of replicas and others.
bitbucket_installation_timeout = 30

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
