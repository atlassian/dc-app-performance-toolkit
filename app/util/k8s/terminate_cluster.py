import logging
from argparse import ArgumentParser
from datetime import datetime, timedelta
from time import sleep, time

import boto3
import botocore
from boto3.exceptions import Boto3Error
from botocore import exceptions

US_EAST_2 = "us-east-2"
US_EAST_1 = "us-east-1"
REGIONS = [US_EAST_2, US_EAST_1]


def is_float(element):
    try:
        float(element)
        return True
    except ValueError:
        return False


def wait_for_node_group_delete(eks_client, cluster_name, node_group):
    timeout = 900  # 15 min
    attempt = 0
    sleep_time = 10
    attempts = timeout // sleep_time

    while attempt < attempts:
        try:
            status_info = eks_client.describe_nodegroup(clusterName=cluster_name, nodegroupName=node_group)['nodegroup']
        except eks_client.exceptions.ResourceNotFoundException:
            logging.info(f"Node group {node_group} for cluster {cluster_name} was successfully deleted.")
            break
        if status_info['status'] == "DELETING":
            logging.info(f"Node group {node_group} for cluster {cluster_name} status is {status_info['status']}. "
                         f"Attempt {attempt}/{attempts}. Sleeping {sleep_time} seconds.")

            sleep(sleep_time)
            attempt += 1
        else:
            logging.error(f"Node group {node_group} for cluster {cluster_name} has "
                          f"unexpected status: {status_info['status']}.")
            logging.error(f"Health status: {status_info['health']}")
            return
    else:
        logging.error(f"Node group {node_group} for cluster {cluster_name} was not deleted in {timeout} seconds.")


def wait_for_cluster_delete(eks_client, cluster_name):
    timeout = 600  # 10 min
    attempt = 0
    sleep_time = 10
    attempts = timeout // sleep_time

    while attempt < attempts:
        try:
            status = eks_client.describe_cluster(name=cluster_name)['cluster']['status']
        except eks_client.exceptions.ResourceNotFoundException:
            logging.info(f"Cluster {cluster_name} was successfully deleted.")
            break
        logging.info(f"Cluster {cluster_name} status is {status}. "
                     f"Attempt {attempt}/{attempts}. Sleeping {sleep_time} seconds.")
        sleep(sleep_time)
        attempt += 1
    else:
        logging.error(f"Cluster {cluster_name} was not deleted in {timeout} seconds.")


def wait_for_rds_delete(rds_client, db_name):
    timeout = 600  # 10 min
    attempt = 0
    sleep_time = 10
    attempts = timeout // sleep_time

    while attempt < attempts:
        try:
            status = \
                rds_client.describe_db_instances(DBInstanceIdentifier=db_name)['DBInstances'][0]['DBInstanceStatus']
        except rds_client.exceptions.DBInstanceNotFoundFault:
            logging.info(f"RDS {db_name} was successfully deleted.")
            break
        logging.info(f"RDS {db_name} status is {status}. "
                     f"Attempt {attempt}/{attempts}. Sleeping {sleep_time} seconds.")
        sleep(sleep_time)
        attempt += 1
    else:
        logging.error(f"RDS {db_name} was not deleted in {timeout} seconds.")


def delete_nodegroup(aws_region, cluster_name):
    try:
        eks_client = boto3.client('eks', region_name=aws_region)
        autoscaling_client = boto3.client('autoscaling', region_name=aws_region)
        node_groups = eks_client.list_nodegroups(clusterName=cluster_name)['nodegroups']

        if node_groups:
            for node_group in node_groups:
                autoscaling_group_name = None
                try:
                    autoscaling_group_name = eks_client.describe_nodegroup(
                        clusterName=cluster_name,
                        nodegroupName=node_group)['nodegroup']['resources']['autoScalingGroups'][0]['name']
                    autoscaling_client.delete_auto_scaling_group(AutoScalingGroupName=autoscaling_group_name,
                                                                 ForceDelete=True)
                except Boto3Error as e:
                    logging.error(f"Deleting autoscaling group {autoscaling_group_name} failed with error: {e}")

                try:
                    eks_client.delete_nodegroup(clusterName=cluster_name, nodegroupName=node_group)
                    wait_for_node_group_delete(eks_client, cluster_name, node_group)
                except Boto3Error as e:
                    logging.error(f"Deleting node group {node_group} failed with error: {e}")
        else:
            logging.info(f"Cluster {cluster_name} does not have nodegroups.")
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            logging.info(f"No cluster found for name: {cluster_name}")
        else:
            raise e


def delete_cluster(aws_region, cluster_name):
    try:
        eks_client = boto3.client('eks', region_name=aws_region)
        eks_client.delete_cluster(name=cluster_name)
        wait_for_cluster_delete(eks_client, cluster_name)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            logging.info(f"No cluster found for name: {cluster_name}")
        else:
            raise e


def delete_lb(aws_region, vpc_id):
    elb_client = boto3.client('elb', region_name=aws_region)
    try:
        lb_names = [lb['LoadBalancerName']
                    for lb in elb_client.describe_load_balancers()['LoadBalancerDescriptions']
                    if lb['VPCId'] == vpc_id]
    except exceptions.EndpointConnectionError as e:
        logging.error(f"Could not connect to the ELBv2 endpoint URL: {e}")
        return
    if lb_names:
        for lb_name in lb_names:
            try:
                logging.info(f"Deleting load balancer: {lb_name} for vpc id: {vpc_id}")
                elb_client.delete_load_balancer(LoadBalancerName=lb_name)
            except Boto3Error as e:
                logging.error(f"Deleting load balancer {lb_name} failed with error: {e}")


def wait_for_nat_gateway_delete(ec2, nat_gateway_id):
    timeout = 600  # 10 min
    attempt = 0
    sleep_time = 10
    attempts = timeout // sleep_time

    while attempt < attempts:
        try:
            status = ec2.describe_nat_gateways(NatGatewayIds=[nat_gateway_id])['NatGateways'][0]['State']
        except ec2.exceptions.ResourceNotFoundException:
            logging.info(f"NAT gateway with id {nat_gateway_id} was not found.")
            break

        if status == 'deleted':
            logging.info(f"NAT gateway with id {nat_gateway_id} was successfully deleted.")
            break

        logging.info(f"NAT gateway with id {nat_gateway_id} status is {status}. "
                     f"Attempt {attempt}/{attempts}. Sleeping {sleep_time} seconds.")
        sleep(sleep_time)
        attempt += 1

    else:
        logging.error(f"NAT gateway with id {nat_gateway_id} was not deleted in {timeout} seconds.")


def delete_nat_gateway(aws_region, vpc_id):
    ec2_client = boto3.client('ec2', region_name=aws_region)
    filters = [{'Name': 'vpc-id', 'Values': [f'{vpc_id}', ]}, ]
    try:
        nat_gateway = ec2_client.describe_nat_gateways(Filters=filters)
    except exceptions.EndpointConnectionError as e:
        logging.error(f"Could not retrieve NAT gateways: {e}")
        return
    nat_gateway_ids = [nat['NatGatewayId'] for nat in nat_gateway['NatGateways']]
    if nat_gateway_ids:
        for nat_gateway_id in nat_gateway_ids:
            logging.info(f"Deleting NAT gateway with id: {nat_gateway_id}")
            try:
                ec2_client.delete_nat_gateway(NatGatewayId=nat_gateway_id)
                wait_for_nat_gateway_delete(ec2_client, nat_gateway_id)
            except Boto3Error as e:
                logging.error(f"Deleting NAT gateway with id {nat_gateway_id} failed with error: {e}")


def delete_igw(ec2_resource, vpc_id):
    vpc_resource = ec2_resource.Vpc(vpc_id)
    igws = vpc_resource.internet_gateways.all()
    if igws:
        for igw in igws:
            for retry in range(5):
                try:
                    logging.info(f"Detaching and Removing igw id: {igw.id}")
                    igw.detach_from_vpc(
                        VpcId=vpc_id
                    )
                    igw.delete()
                    break
                except exceptions.ClientError as e:
                    if "Network vpc-" in str(e) and "has some mapped public address(es)" in str(e):
                        logging.warning(f"Detaching igw failed with error: {e}. Retrying in 1 minute...")
                        sleep(120)
                except Boto3Error as e:
                    logging.error(f"Deleting igw failed with error: {e}")


def delete_subnets(ec2_resource, vpc_id):
    vpc_resource = ec2_resource.Vpc(vpc_id)
    subnets_all = vpc_resource.subnets.all()
    subnets = [ec2_resource.Subnet(subnet.id) for subnet in subnets_all]

    if subnets:
        try:
            for sub in subnets:
                logging.info(f"Removing subnet with id: {sub.id}")
                sub.delete()
        except Boto3Error as e:
            logging.error(f"Delete of subnet failed with error: {e}")


def delete_route_tables(ec2_resource, vpc_id):
    vpc_resource = ec2_resource.Vpc(vpc_id)
    rtbs = vpc_resource.route_tables.all()
    if rtbs:
        try:
            for rtb in rtbs:
                if rtb.associations_attribute and rtb.associations_attribute[0]['Main'] == True:
                    logging.info(f"{rtb.id} is the main route table, skipping...")
                    continue
                logging.info(f"Removing rtb-id: {rtb.id}")
                table = ec2_resource.RouteTable(rtb.id)
                table.delete()
        except Boto3Error as e:
            logging.error(f"Delete of route table failed with error: {e}")


def delete_security_groups(ec2_resource, vpc_id):
    vpc_resource = ec2_resource.Vpc(vpc_id)
    sgps = vpc_resource.security_groups.all()
    if sgps:
        try:
            for sg in sgps:
                if sg.group_name == 'default':
                    logging.info(f"{sg.id} is the default security group, skipping...")
                    continue
                if sg.ip_permissions:
                    logging.info(f"Removing ingress rules for security group with id: {sg.id}")
                    sg.revoke_ingress(IpPermissions=sg.ip_permissions)
                if sg.ip_permissions_egress:
                    logging.info(f"Removing egress rules for security group with id: {sg.id}")
                    sg.revoke_egress(IpPermissions=sg.ip_permissions_egress)
            for sg in sgps:
                if sg.group_name == 'default':
                    logging.info(f"{sg.id} is the default security group, skipping...")
                    continue
                logging.info(f"Removing security group with id: {sg.id}")
                sg.delete()
        except Boto3Error as e:
            logging.error(f"Delete of security group failed with error: {e}")


def get_vpc_region_by_name(vpc_name):
    for rgn in REGIONS:
        ec2_resource = boto3.resource('ec2', region_name=rgn)
        filters = [{'Name': 'tag:Name', 'Values': [vpc_name]}]
        vpc = list(ec2_resource.vpcs.filter(Filters=filters))
        if vpc:
            return rgn
        logging.info(f"VPC {vpc_name} NOT found in {rgn} region.")

    logging.warning(f"VPC {vpc_name} NOT found in the following regions: {REGIONS}.")


def delete_rds(aws_region, vpc_id):
    rds_client = boto3.client('rds', region_name=aws_region)
    try:
        db_instances = rds_client.describe_db_instances()['DBInstances']
    except exceptions.EndpointConnectionError as e:
        logging.error(f"Could not connect to the RDS endpoint URL: {e}")
        return
    db_names_and_subnets = [(db_instance['DBInstanceIdentifier'], db_instance['DBSubnetGroup']['DBSubnetGroupName'])
                            for db_instance in db_instances
                            if vpc_id == db_instance['DBSubnetGroup']['VpcId']]
    for db_name, subnet_name in db_names_and_subnets:
        try:
            logging.info(f"Deleting RDS {db_name} for VPC id: {vpc_id}.")
            rds_client.delete_db_instance(
                DBInstanceIdentifier=db_name, SkipFinalSnapshot=True, DeleteAutomatedBackups=True)
            wait_for_rds_delete(rds_client, db_name)
            logging.info(f"Deleting RDS subnet group {subnet_name}")
            rds_client.delete_db_subnet_group(DBSubnetGroupName=subnet_name)
        except Boto3Error as e:
            logging.error(f"Delete RDS {db_name} failed with error: {e}")


def terminate_vpc(vpc_name, aws_region=None):
    if not aws_region:
        aws_region = get_vpc_region_by_name(vpc_name)

    if aws_region:
        ec2_resource = boto3.resource('ec2', region_name=aws_region)
        filters = [{'Name': 'tag:Name', 'Values': [vpc_name]}]
        vpc = list(ec2_resource.vpcs.filter(Filters=filters))
        if not vpc:
            logging.warning(f"VPC {vpc_name} NOT found in region {aws_region}.")
            return
        vpc_id = vpc[0].id
        logging.info(f"Checking RDS for VPC {vpc_name}.")
        delete_rds(aws_region, vpc_id)

        logging.info(f"Checking load balancers for VPC {vpc_name}.")
        delete_lb(aws_region, vpc_id)

        logging.info(f"Checking NAT gateway for VPC {vpc_name}.")
        delete_nat_gateway(aws_region, vpc_id)

        logging.info(f"Checking internet gateway for VPC {vpc_name}.")
        delete_igw(ec2_resource, vpc_id)

        logging.info(f"Checking subnets for VPC {vpc_name}.")
        delete_subnets(ec2_resource, vpc_id)

        logging.info(f"Checking route tables for VPC {vpc_name}.")
        delete_route_tables(ec2_resource, vpc_id)

        logging.info(f"Checking security groups for VPC {vpc_name}.")
        delete_security_groups(ec2_resource, vpc_id)

        logging.info(f"Deleting VPC {vpc_name}.")
        try:
            ec2_resource.Vpc(vpc_id).delete()
        except Boto3Error as e:
            logging.error(f"Deleting VPC {vpc_name} failed with error: {e}.")

        logging.info(f"Release EIP for {vpc_name}.")
        release_eip(aws_region, vpc_name)


def get_cluster_region_by_name(cluster_name):
    for rgn in REGIONS:
        eks_client = boto3.client('eks', region_name=rgn)
        clusters = eks_client.list_clusters()['clusters']
        if cluster_name in clusters:
            logging.info(f"Cluster {cluster_name} found in {rgn} region.")
            return rgn
        else:
            logging.info(f"Cluster {cluster_name} NOT found in {rgn} region.")

    logging.warning(f"Cluster {cluster_name} NOT found in the following regions: {REGIONS}.")


def terminate_cluster(cluster_name, aws_region=None):
    # If no region is provided, get the region by cluster name
    if not aws_region:
        aws_region = get_cluster_region_by_name(cluster_name)

    if not aws_region:
        raise ValueError("Could not determine the AWS region for the given cluster name.")

    # Delete the nodegroup and cluster in the specified region
    delete_nodegroup(aws_region, cluster_name)
    delete_cluster(aws_region, cluster_name)


def release_eip(aws_region, vpc_name):
    ec2_client = boto3.client('ec2', region_name=aws_region)
    addresses_dict = ec2_client.describe_addresses()
    for eip_dict in addresses_dict['Addresses']:
        if not eip_dict.get("Tags"):
            logging.warning(f"EIP {eip_dict['AllocationId']} does not have tags. Review and terminate manually.")
            return
        name = next((tag["Value"] for tag in eip_dict["Tags"] if tag["Key"] == "Name"), None)
        if name and vpc_name in name:
            logging.info(f"Releasing EIP {eip_dict['PublicIp']} with name: {name}")
            ec2_client.release_address(AllocationId=eip_dict['AllocationId'])


def retrieve_ebs_volumes(aws_region, cluster_name):
    ec2 = boto3.resource('ec2', aws_region)
    volumes = []

    # Get all volumes in the region
    response = ec2.volumes.all()

    for volume in response:
        # Check if the volume is in use
        if volume.state == "in-use":
            logging.info(f"Volume {volume.id} is in use: skipping")
        else:
            # Check if the volume has the cluster_name in any of its tag values
            cluster_tag = next((tag["Value"] for tag in volume.tags if cluster_name in tag["Value"]), None)
            if cluster_tag:
                volumes.append(volume.id)

            # Check for 'dynamic-pvc' or 'nfs-shared-home' in the name
            name = next((tag["Value"] for tag in volume.tags if tag["Key"] == "Name"), None)
            if "dynamic-pvc" in name or "nfs-shared-home" in name:
                logging.info(f"Volume {volume.id} is not in use and "
                             f"has 'dynamic-pvc' or 'nfs-shared-home' in name: deleting...")
                volumes.append(volume.id)

    print(f"Found volumes: {volumes}")
    return volumes


def delete_ebs_volumes_by_id(aws_region, volumes):
    ec2 = boto3.resource('ec2', aws_region)

    # Terminate the volumes
    for volume_id in volumes:
        try:
            volume = ec2.Volume(volume_id)
            if volume.state == "in-use":
                print(f"Volume {volume_id} is in use: skipping")
                continue
            volume.delete()
            print(f"Terminated volume: {volume_id}")
        except Exception as e:
            print(f"Failed to terminate volume {volume_id}: {e}")


def get_clusters_to_terminate():
    clusters_to_terminate = []
    for rgn in REGIONS:
        eks_client = boto3.client('eks', region_name=rgn)
        clusters = eks_client.list_clusters()['clusters']
        for cluster in clusters:
            cluster_info = eks_client.describe_cluster(name=cluster)['cluster']
            created_date = cluster_info['createdAt']
            persist_days = cluster_info['tags'].get('persist_days', 0)
            if not is_float(persist_days):
                persist_days = 0
            created_date_timestamp = created_date.timestamp()
            persist_seconds = float(persist_days) * 24 * 60 * 60
            now = time()
            if created_date_timestamp + persist_seconds > now:
                logging.info(f"Cluster {cluster} is not EOL yet, skipping...")
            else:
                logging.info(f"Cluster {cluster} is EOL and should be deleted.")
                clusters_to_terminate.append(cluster)
    return clusters_to_terminate


def terminate_open_id_providers(cluster_name=None):
    iam_client = boto3.client('iam')
    providers = iam_client.list_open_id_connect_providers()['OpenIDConnectProviderList']
    for provider in providers:
        tags = iam_client.list_open_id_connect_provider_tags(OpenIDConnectProviderArn=provider['Arn'])['Tags']
        created_date = iam_client.get_open_id_connect_provider(OpenIDConnectProviderArn=provider['Arn'])['CreateDate']

        name = next((tag["Value"] for tag in tags if tag["Key"] == "Name"), None)
        if name and cluster_name and cluster_name in name:
            logging.info(f"Deleting Open ID provider with name: {name}")
            iam_client.delete_open_id_connect_provider(OpenIDConnectProviderArn=provider['Arn'])
            return
        if name == 'Alfred':
            logging.info(f"Skipping Alfred Open ID provider")
            continue
        persist_days = next((tag["Value"] for tag in tags if tag["Key"] == "persist_days"), None)
        if persist_days:
            if not is_float(persist_days):
                persist_days = 0
            created_date_timestamp = created_date.timestamp()
            persist_seconds = float(persist_days) * 24 * 60 * 60
            now = time()
            if created_date_timestamp + persist_seconds > now:
                logging.info(f"Open ID provider {name} is not EOL yet, skipping...")
            else:
                logging.info(f"Open ID provider {name} is EOL and should be deleted.")
                iam_client.delete_open_id_connect_provider(OpenIDConnectProviderArn=provider['Arn'])


def retrieve_open_identities(cluster_name, aws_region):
    open_identities = []

    try:
        eks_client = boto3.client("eks", region_name=aws_region)
        response = eks_client.describe_cluster(name=cluster_name)

        identity_provider = response["cluster"]["identity"]["oidc"]["issuer"]
        identity_id = identity_provider.split('/id/')[-1]
        open_identities.append(identity_id)
        print(f"Open identity providers: {open_identities}")
    except Exception as e:
        print(f"Failed to retrieve Open identity providers from {cluster_name}. Skipping...")
        print(f"Error details: {e}")

    return open_identities


def delete_open_identities_for_cluster(open_identities):
    if not open_identities:
        print("No OpenID Connect providers to delete.")
        return

    iam_client = boto3.client('iam')

    for identity in open_identities:
        try:
            providers = iam_client.list_open_id_connect_providers()['OpenIDConnectProviderList']
            for provider in providers:
                provider_identity_id = provider['Arn'].split('/id/')[-1]
                if provider_identity_id == identity:
                    iam_client.delete_open_id_connect_provider(OpenIDConnectProviderArn=provider['Arn'])
                    print(f"Deleted identity provider: {identity}")
                else:
                    print(f"Identity '{identity}' not found in provider '{provider['Arn']}'")
        except Exception as e:
            print(f"Failed to delete identity provider: {identity}")
            print(f"Error details: {e}")


def get_vpcs_to_terminate():
    vpcs_to_terminate = []
    for rgn in REGIONS:
        ec2_resource = boto3.resource('ec2', region_name=rgn)
        vpcs = ec2_resource.vpcs.all()
        for vpc in vpcs:

            if vpc.is_default:
                logging.info(f"Skipping default VPC for {rgn} region with id: {vpc.id}")
                continue

            vpc_name = next((tag["Value"] for tag in vpc.tags if tag["Key"] == "Name"), None)
            if "Atlassian-Standard-Infrastructure" in vpc_name:
                logging.info(f"Skipping ASI CloudFormation VPC for {rgn} region with id: {vpc.id}")
                continue

            # mark for remove all VPC without instances
            if not list(vpc.instances.all()):
                cluster_name = vpc_name.replace("-vpc", "-cluster")
                if cluster_name in boto3.client('eks', region_name=rgn).list_clusters()['clusters']:
                    logging.info(f"Skipping VPC {vpc_name}, because this vpc has a cluster...")
                    continue
                logging.info(f"VPC {vpc_name} tagged for termination.")
                vpcs_to_terminate.append(vpc_name)

    return vpcs_to_terminate


def release_unused_eips():
    for rgn in REGIONS:
        ec2_client = boto3.client('ec2', region_name=rgn)
        addresses_dict = ec2_client.describe_addresses()
        for eip_dict in addresses_dict['Addresses']:
            if "NetworkInterfaceId" not in eip_dict:
                eip_name = next((tag["Value"] for tag in eip_dict["Tags"] if tag["Key"] == "Name"), None)
                cluster_name = eip_name.split("-vpc")[0] + "-cluster"
                if cluster_name in boto3.client('eks', region_name=rgn).list_clusters()['clusters']:
                    logging.info(f"Skipping EIP {eip_name}, because this EIP has a cluster...")
                    continue
                logging.info(f"Releasing EIP {eip_dict['PublicIp']} with name: {eip_name}")
                ec2_client.release_address(AllocationId=eip_dict['AllocationId'])


def role_filter(role):
    if role["RoleName"].startswith("atlas-"):
        tags = boto3.client("iam").list_role_tags(RoleName=role["RoleName"])
        persist_days = None
        for tag in tags["Tags"]:
            if tag["Key"] == "persist_days":
                try:
                    persist_days = float(tag["Value"])
                except ValueError:
                    ...
        if persist_days:
            eol_time = role['CreateDate'] + timedelta(days=float(persist_days))
            return datetime.now(role['CreateDate'].tzinfo) > eol_time
    return False


def remove_cluster_specific_roles_and_policies(cluster_name, aws_region):
    iam_client = boto3.client("iam", region_name=aws_region)

    # Get and filter roles by cluster name prefix
    all_roles = iam_client.list_roles()
    cluster_roles = [role for role in all_roles["Roles"] if role["RoleName"].startswith(cluster_name)]

    for role in cluster_roles:
        role_name = role["RoleName"]

        attached_policies = iam_client.list_attached_role_policies(RoleName=role_name)

        for policy in attached_policies["AttachedPolicies"]:
            # Detach policy from the role
            iam_client.detach_role_policy(RoleName=role_name, PolicyArn=policy["PolicyArn"])
            print(f"  Detached policy {policy['PolicyName']} from role {role_name}")

            if cluster_name in policy['PolicyName']:
                # Delete the policy
                iam_client.delete_policy(PolicyArn=policy["PolicyArn"])
                print(f"  Deleted policy {policy['PolicyName']}")

        # Delete the role
        iam_client.delete_role(RoleName=role_name)
        print(f"Deleted Role: {role_name}")


def remove_role_and_policies(role_name, active_clusters):
    if role_name.startswith(tuple(active_clusters)):
        logging.info(f"There is an active cluster which can be using role {role_name}. Skip.")
        return
    logging.info(f"Role {role_name} is EOL and should be deleted.")
    iam_client = boto3.client("iam")
    attached_policies = iam_client.list_attached_role_policies(RoleName=role_name).get("AttachedPolicies")
    for policy in attached_policies:
        logging.info(f"Detach {policy['PolicyArn']} from {role_name}")
        iam_client.detach_role_policy(PolicyArn=policy["PolicyArn"], RoleName=role_name)
        if policy["PolicyName"].endswith("_Fleet-Enrollment") or policy["PolicyName"].endswith("_LaaS-policy"):
            logging.info(f"Delete policy {policy['PolicyName']}")
            iam_client.delete_policy(PolicyArn=policy["PolicyArn"])
    logging.info(f"Delete role {role_name}")
    iam_client.delete_role(RoleName=role_name)
    logging.info(f"Role {role_name} deleted successfully")


def get_role_names_to_terminate():
    iam_client = boto3.client("iam")
    roles_paginated = iam_client.list_roles(MaxItems=1000)
    all_roles = roles_paginated["Roles"]
    while roles_paginated.get("Marker"):
        roles_paginated = iam_client.list_roles(Marker=roles_paginated["Marker"], MaxItems=1000)
        all_roles.extend(roles_paginated["Roles"])
    logging.info(f"Roles count: {len(all_roles)}")
    filtered_roles = list(filter(role_filter, all_roles))
    return list(map(lambda role: role["RoleName"], filtered_roles))


def delete_unused_volumes():
    for rgn in REGIONS:
        logging.info(f"Region: {rgn}")
        ec2_resource = boto3.resource('ec2', region_name=rgn)
        volumes = ec2_resource.volumes.all()
        # Filter unused volumes
        for volume in volumes:
            if volume.state == "in-use":
                logging.info(f"Volume {volume.id} is in use: skipping")
            else:
                if not volume.tags:
                    logging.warning(f"Volume {volume} does not have tags!")
                    continue
                # Delete unused volumes with specific tags or names
                persist_days = next((tag["Value"] for tag in volume.tags if tag["Key"] == "persist_days"), None)
                if persist_days:
                    eol_time = volume.create_time + timedelta(days=float(persist_days))
                    if datetime.now(volume.create_time.tzinfo) < eol_time:
                        logging.info(f"Volume {volume.id} is not EOL yet, skipping...")
                    else:
                        logging.info(f"Volume {volume.id} is EOL, deleting...")
                        volume.delete()
                else:
                    name = next((tag["Value"] for tag in volume.tags if tag["Key"] == "Name"), None)
                    if "dynamic-pvc" or "nfs-shared-home" in name:
                        logging.info(f"Volume {volume.id} is not in use and "
                                     f"has 'dynamic-pvc' or 'nfs-shared-home' in name: deleting...")
                        volume.delete()
                    else:
                        logging.warning(f"Volume {volume.id} does not have 'persist_days' tag "
                                        f"| Name tag {name}: skipping")


def main():
    parser = ArgumentParser()
    parser.add_argument("--cluster_name", type=str, help='Cluster name to terminate.')
    parser.add_argument('--aws_region', type=str, help='AWS region where the cluster is located (e.g., "us-east-2").')
    parser.add_argument('--all', action='store_true', help='Terminate all clusters in all regions.')
    args = parser.parse_args()

    if not args.all:
        if not args.cluster_name:
            raise SystemExit("--cluster_name argument is not provided.")
        if not args.aws_region:
            raise SystemExit("--aws_region argument is not provided.")

    if args.cluster_name and args.aws_region:
        logging.info(f"Delete all resources for cluster {args.cluster_name}.")
        open_identities = retrieve_open_identities(cluster_name=args.cluster_name, aws_region=args.aws_region)
        terminate_cluster(cluster_name=args.cluster_name, aws_region=args.aws_region)
        vpc_name = f'{args.cluster_name.replace("-cluster", "-vpc")}'
        logging.info(f"Delete VPC for cluster {args.cluster_name}.")
        terminate_vpc(vpc_name=vpc_name, aws_region=args.aws_region)
        volumes = retrieve_ebs_volumes(aws_region=args.aws_region, cluster_name=args.cluster_name)
        delete_open_identities_for_cluster(open_identities)
        remove_cluster_specific_roles_and_policies(cluster_name=args.cluster_name, aws_region=args.aws_region)
        delete_ebs_volumes_by_id(aws_region=args.aws_region, volumes=volumes)
        return

    logging.info(f"--cluster_name parameter was not specified.")
    logging.info("Searching for clusters to remove.")
    clusters = get_clusters_to_terminate()
    for cluster_name in clusters:
        logging.info(f"Delete all resources and VPC for cluster {cluster_name}.")
        terminate_cluster(cluster_name=cluster_name)
        vpc_name = f'{cluster_name.replace("-cluster", "-vpc")}'
        terminate_vpc(vpc_name=vpc_name)
        terminate_open_id_providers(cluster_name=cluster_name)
    vpcs = get_vpcs_to_terminate()
    for vpc_name in vpcs:
        logging.info(f"Delete all resources for vpc {vpc_name}.")
        terminate_vpc(vpc_name=vpc_name)
    logging.info("Release unused EIPs")
    release_unused_eips()
    logging.info("Terminate open ID providers")
    terminate_open_id_providers()
    role_names = get_role_names_to_terminate()
    active_clusters = []
    for region in REGIONS:
        eks_client = boto3.client("eks", region_name=region)
        active_clusters.extend(eks_client.list_clusters().get("clusters"))
    for role_name in role_names:
        remove_role_and_policies(role_name, active_clusters)
    logging.info("Terminate unused and expired ebs volumes")
    delete_unused_volumes()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
