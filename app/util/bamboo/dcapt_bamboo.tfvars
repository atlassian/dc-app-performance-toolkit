# This file configures the Terraform for Atlassian Bamboo DC on Kubernetes for Data Center App Performance Toolkit.
# Please configure this file carefully before installing the infrastructure.
# Do not change the defaults.
# See https://developer.atlassian.com/platform/marketplace/dc-apps-performance-toolkit-user-guide-bamboo/ for more information.

################################################################################
# Mandatory
################################################################################

# 'environment_name' provides your environment a unique name within a single cloud provider account.
# This value can not be altered after the configuration has been applied.
# WARNING: use only lowercase letters, numbers and `-` dash symbol
environment_name = "<environment>"

# Cloud provider region that this configuration will deploy to, e.g. "us-east-2"
region = "<region>"

# Bamboo license
# To avoid storing license in a plain text file, we recommend storing it in an environment variable prefixed with `TF_VAR_` (i.e. `TF_VAR_bamboo_license`) and keep the below line commented out
# If storing license as plain-text is not a concern for this environment, feel free to uncomment the following line and supply the license here.
# WARNING 1: without a proper enterprise-scale license agents would not be set up correctly
# WARNING 2: if you don't have a valid developer license ask in your DCHELP ticket
# WARNING 3: make sure license inserted below as a one-liner without any spaces or new line characters
bamboo_license = "<license key>"

# Bamboo system admin credentials
# WARNING: This template includes bamboo enterprise-scale dataset (see the `dataset_url` property below), so credentials
# listed below should not be changed before deployment as they used inside dataset.
# After successful deployment it is recommended to change admin credentials via UI configuration page for security reasons.
bamboo_admin_username      = "admin"
bamboo_admin_password      = "admin"
bamboo_admin_display_name  = "administrator"
bamboo_admin_email_address = "admin@example.com"

# URL for DCAPT dataset to import
dataset_url = "https://centaurus-datasets.s3.amazonaws.com/bamboo/dcapt-bamboo.zip"

# Custom tags for all resources to be created. Please add all tags you need to propagate among the resources.
resource_tags = {
  Terraform = "true"
}

# Instance types that is preferred for EKS node group.
instance_types = ["m5.4xlarge"]
# Desired number of nodes that the node group should launch with initially.
desired_capacity = 1

# RDS instance configurable attributes. Note that the allowed value of allocated storage and iops may vary based on instance type.
# You may want to adjust these values according to your needs.
# Documentation can be found via:
# https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html
# https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Storage.html#USER_PIOPS
db_instance_class    = "db.t3.medium"
db_allocated_storage = 100
db_iops              = 1000

# Helm chart version of Bamboo and Bamboo agent instances
bamboo_helm_chart_version       = "1.0.0"
bamboo_agent_helm_chart_version = "1.0.0"

# Bamboo instance resource configuration
bamboo_cpu = "4"
bamboo_mem = "16Gi"
bamboo_min_heap = "256m"
bamboo_max_heap = "512m"

# Bamboo Agent instance resource configuration
bamboo_agent_cpu = "200m"
bamboo_agent_mem = "700m"

# Number of Bamboo remote agents to launch
number_of_bamboo_agents = 50