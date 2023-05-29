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
environment_name = "dcapt-skillsforjira"

# Supported products: jira, confluence, bitbucket and bamboo.
# e.g.: products = ["confluence"]
# ! REQUIRED !
products = ["jira"]

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
# Please make sure valid confluence license is used without spaces and new line symbols.
# ! REQUIRED !
jira_license = "AAAB3Q0ODAoPeNp9kttvolAQxt/5K0j2ZTcbkItVMSFZC6yr4dIVbGvSl1Mc9Vi5ZDjY4l+/3IxutT4e+GbmN9833/w85h1S8MqAl7vDrjpUFd4wA16RFJV7g+IRMKNJrMs9SepLA1WVuTUCxJskTQFFm4YQZ2AtKatUlhtYs4fZxLc4N49eAb3VPCs76ILMGUnMSMhcEoGOcFgT/MUSBpG4hD23pUjEi5KHHMMNycAkDPSKSJDuBEXj2qlBkULdzvAcx5oZk5F9/GV9pBSLs7qeoAyOCJZD6O6SwQfcA05M/f5ZUgRt4cnCxB30BNu7GzeAKSbLPGRi9RCyZMXeCYJYdqR70BnmcEtWwhADYgbYSHcN6R+SbXTHkIzf5sfqMGXzv74U5j26PRh438exokaFOtrMR2/x02IRdmHdcWcRLIrO00/tvTPdBuPwRef8/DULkaZ1DCeUr/O5kuI1P0urSuSYxOEXnt7Y+CLPdk5psT0xfcsVbFnrqlq/LzdtPltUSvQrsuvTfEawqlyRXQach2sS04zUawdVxrxZZmwg1J8+X1QbxvHalf/sqYlSpFkbsgknq6clA++3DPz3agO+WeHHy5C39mSX1wMb8otTueH8OcF53aln8/4H0ZVKvDAsAhQ2bqlvU67m5Of0S8mLBkls+wpxqAIUC8U5UIJu0bMOwnlpjM3TdBaQ6p0=X02mm"

# Number of Jira/JSM application nodes
# Note: For initial installation this value needs to be set to 1 and it can be changed only after Jira is fully
# installed and configured.
jira_replica_count = 1

# Supported versions by DCAPT: https://github.com/atlassian/dc-app-performance-toolkit#supported-versions
#
# Jira version
jira_version_tag = "9.4.4"
# JSM version
# jira_version_tag = "4.20.20"

# Shared home restore configuration.
# Make sure Jira/JSM version set in `jira_version_tag` match the snapshot version.
#
# Jira 8.20.20 DCAPT large dataset EBS snapshot
#jira_shared_home_snapshot_id = "snap-001cb5a5d63b1a016"
# Jira 9.4.4 DCAPT large dataset EBS snapshot
jira_shared_home_snapshot_id = "snap-0ae3cf75516d1ce0c"
# JSM 4.20.20 DCAPT large dataset EBS snapshot
# jira_shared_home_snapshot_id = "snap-012d40647b2ffa6eb	"
# JSM 5.4.4 DCAPT large dataset EBS snapshot
# jira_shared_home_snapshot_id = "snap-01ffbdc7ce1be745f"

# Database restore configuration.
# Make sure Jira/JSM version set in `jira_version_tag` match the snapshot version.
# Build number stored within the snapshot and Jira license are also required, so that Jira can be fully setup prior to start.
#
# Jira 8.20.20 DCAPT large dataset RDS snapshot
# jira_db_snapshot_id = "arn:aws:rds:us-east-2:585036043680:snapshot:dcapt-jira-8-20-20"
# Jira 9.4.4 DCAPT large dataset RDS snapshot
jira_db_snapshot_id = "arn:aws:rds:us-east-2:585036043680:snapshot:dcapt-jira-9-4-4"
# JSM 4.20.20 DCAPT large dataset RDS snapshot
# jira_db_snapshot_id = "arn:aws:rds:us-east-2:585036043680:snapshot:dcapt-jsm-4-20-20"
# JSM 5.4.4 DCAPT large dataset RDS snapshot
# jira_db_snapshot_id = "arn:aws:rds:us-east-2:585036043680:snapshot:dcapt-jsm-5-4-20"

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

# 
# # If you restore the database, make sure `jira_db_name' is set to the db name from the snapshot.
# # Set `null` if the snapshot does not have a default db name.
jira_db_name = "jira_dcapt"

# 
# # The master user credential for the database instance.
# # If username is not provided, it'll be default to "postgres".
# # If password is not provided, a random password will be generated.
jira_db_master_username = "atljira"
jira_db_master_password = "Password1!"