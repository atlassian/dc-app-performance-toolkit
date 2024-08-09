import logging
from argparse import ArgumentParser
from datetime import datetime, timedelta
from time import sleep, time

import boto3
import botocore
from boto3.exceptions import Boto3Error
from botocore import exceptions

from retry import retry

DEFAULT_RETRY_COUNT = 3
DEFAULT_RETRY_DELAY = 10

US_EAST_2 = "us-east-2"
US_EAST_1 = "us-east-1"
REGIONS = [US_EAST_2, US_EAST_1]


def is_float(element):
    try:
        float(element)
        return True
    except ValueError:
        return False


def retrieve_environment_name(cluster_name):
    if cluster_name.endswith('-cluster'):
        cluster_name = cluster_name[:-(len('-cluster'))]
    if cluster_name.startswith('atlas-'):
        cluster_name = cluster_name[len('atlas-'):]
    return cluster_name


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


def wait_for_hosted_zone_delete(route53_client, hosted_zone_id):
    timeout = 600  # 10 min
    attempt = 0
    sleep_time = 10
    attempts = timeout // sleep_time

    while attempt < attempts:
        try:
            route53_client.get_hosted_zone(Id=hosted_zone_id)
        except route53_client.exceptions.NoSuchHostedZone:
            logging.info(f"Hosted zone {hosted_zone_id} was successfully deleted.")
            break
        logging.info(f"Hosted zone {hosted_zone_id} still exists. "
                     f"Attempt {attempt}/{attempts}. Sleeping {sleep_time} seconds.")
        sleep(sleep_time)
        attempt += 1
    else:
        logging.error(f"Hosted zone {hosted_zone_id} was not deleted in {timeout} seconds.")


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


def wait_for_network_interface_to_be_detached(ec2_client, network_interface_id):
    timeout = 600  # 10 min
    attempt = 0
    sleep_time = 10
    attempts = timeout // sleep_time

    while attempt < attempts:
        try:
            status = ec2_client.describe_network_interfaces(
                NetworkInterfaceIds=[network_interface_id])['NetworkInterfaces'][0]['Attachment']['Status']
            if status != 'attached':
                return
        except Exception as e:
            logging.info(f"Unexpected error occurs during detaching the network interface {network_interface_id}, {e}")
            break
        logging.info(f"Network interface {network_interface_id} is in status {status}. "
                     f"Attempt {attempt}/{attempts}. Sleeping {sleep_time} seconds.")
        sleep(sleep_time)
        attempt += 1
    else:
        logging.error(f"Network interface {network_interface_id} is not detached in {timeout} seconds.")


def delete_record_from_hosted_zone(route53_client, hosted_zone_id, record):
    change_batch = {
        'Changes': [
            {
                'Action': 'DELETE',
                'ResourceRecordSet': record
            }
        ]
    }
    try:
        route53_client.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch=change_batch
        )
        logging.info(f"Record {record['Name']} was successfully deleted from hosted zone {hosted_zone_id}.")
    except Exception as e:
        logging.error(f'Unexpected error occurs, could not delete record from hosted zone {hosted_zone_id}: {e}')


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
                except (Boto3Error, KeyError) as e:
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


def delete_hosted_zone_record_if_exists(aws_region, cluster_name):
    environment_name = cluster_name.replace('atlas-', '').replace('-cluster', '')
    eks_client = boto3.client('eks', region_name=aws_region)
    elb_client = boto3.client('elb', region_name=aws_region)
    acm_client = boto3.client('acm', region_name=aws_region)
    domain_name = None
    try:
        cluster_info = eks_client.describe_cluster(name=cluster_name)['cluster']
        cluster_vpc_config = cluster_info['resourcesVpcConfig']
        cluster_vpc_id = cluster_vpc_config['vpcId']
        cluster_elb = [lb for lb in elb_client.describe_load_balancers()['LoadBalancerDescriptions']
                       if lb['VPCId'] == cluster_vpc_id]
        if cluster_elb:
            cluster_elb_listeners = cluster_elb[0]['ListenerDescriptions']
            for listener in cluster_elb_listeners:
                if listener['Listener']['Protocol'] == 'HTTPS':
                    if 'SSLCertificateId' in listener['Listener']:
                        certificate_arn = listener['Listener']['SSLCertificateId']
                        certificate_info = acm_client.describe_certificate(
                            CertificateArn=certificate_arn)['Certificate']
                        certificate_domain_name = certificate_info['DomainName']
                        domain_name = certificate_domain_name.replace('*.', '').replace(environment_name, '')
                        break
                    else:
                        return

    except Exception:
        logging.info(f'No hosted zone found for cluster: {cluster_name}')
        return

    if domain_name:
        try:
            route53_client = boto3.client('route53', region_name=aws_region)
            existed_hosted_zones = route53_client.list_hosted_zones()["HostedZones"]
            if not existed_hosted_zones:
                return
            for hosted_zone in existed_hosted_zones:
                if f'{environment_name}{domain_name}.' == hosted_zone['Name']:
                    hosted_zone_to_delete = hosted_zone
                    records_hosted_zone_to_delete = route53_client.list_resource_record_sets(
                        HostedZoneId=hosted_zone['Id'])['ResourceRecordSets']
                    for record in records_hosted_zone_to_delete:
                        if record['Type'] not in ['NS', 'SOA']:
                            delete_record_from_hosted_zone(route53_client, hosted_zone['Id'], record)
                    route53_client.delete_hosted_zone(Id=hosted_zone_to_delete['Id'])
                    wait_for_hosted_zone_delete(route53_client, hosted_zone['Id'])
                    break

            existed_hosted_zones = route53_client.list_hosted_zones()["HostedZones"]
            existed_hosted_zones_ids = [zone["Id"] for zone in existed_hosted_zones]
            for hosted_zone_id in existed_hosted_zones_ids:
                records_set = route53_client.list_resource_record_sets(
                    HostedZoneId=hosted_zone_id)['ResourceRecordSets']
                for record in records_set:
                    if environment_name in record['Name']:
                        delete_record_from_hosted_zone(route53_client, hosted_zone_id, record)
        except Exception as e:
            logging.error(f"Unexpected error occurs: {e}")


@retry(Exception, tries=DEFAULT_RETRY_COUNT, delay=DEFAULT_RETRY_DELAY)
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


@retry(Exception, tries=DEFAULT_RETRY_COUNT, delay=DEFAULT_RETRY_DELAY)
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


@retry(Exception, tries=DEFAULT_RETRY_COUNT, delay=DEFAULT_RETRY_DELAY)
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


@retry(Exception, tries=12, delay=DEFAULT_RETRY_DELAY)
def delete_subnets(ec2_resource, vpc_id, aws_region):
    vpc_resource = ec2_resource.Vpc(vpc_id)
    subnets_all = vpc_resource.subnets.all()
    subnets = [ec2_resource.Subnet(subnet.id) for subnet in subnets_all]
    if subnets:
        try:
            for sub in subnets:
                logging.info(f"Removing subnet with id: {sub.id}")
                try:
                    ec2_client = boto3.client('ec2', region_name=aws_region)
                    subnet_network_interfaces = ec2_client.describe_network_interfaces(
                        Filters=[{'Name': 'subnet-id', 'Values': [sub.id]}])
                    subnet_network_interfaces = subnet_network_interfaces.get('NetworkInterfaces', [])
                    if subnet_network_interfaces:
                        logging.info(f'VPC {sub.id} has dependency - network interfaces: {subnet_network_interfaces}')
                        for subnet_network_interface in subnet_network_interfaces:
                            delete_network_interface(ec2_client,
                                                     subnet_network_interface['NetworkInterfaceId'])
                    sub.delete()
                except botocore.exceptions.ClientError as e:
                    raise SystemExit(f'Could not delete subnet {sub.id}, {e}')
        except Boto3Error as e:
            logging.error(f"Delete of subnet failed with error: {e}")


@retry(Exception, tries=DEFAULT_RETRY_COUNT, delay=DEFAULT_RETRY_DELAY)
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


@retry(Exception, tries=DEFAULT_RETRY_COUNT, delay=DEFAULT_RETRY_DELAY)
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


def delete_network_interface(ec2_client, network_interface_id):
    timeout = 180  # 3 min
    sleep_time = 10
    attempts = timeout // sleep_time

    for attempt in range(1, attempts):
        try:
            # Attempt to delete the network interface
            ec2_client.delete_network_interface(NetworkInterfaceId=network_interface_id)
            logging.info(f"Network interface {network_interface_id} deleted successfully.")
            return

        except botocore.exceptions.ClientError as e:
            if attempt == attempts:
                raise e
            else:
                logging.info(f"Attempt {attempt}: {e}")
                sleep(sleep_time)


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
    ec2_client = boto3.client('ec2', region_name=aws_region)
    network_interface_id = None

    try:
        db_instances = rds_client.describe_db_instances()['DBInstances']
    except exceptions.EndpointConnectionError as e:
        logging.error(f"Could not connect to the RDS endpoint URL: {e}")
        return
    db_names_and_subnets = [(db_instance['DBInstanceIdentifier'], db_instance['DBSubnetGroup']['DBSubnetGroupName'])
                            for db_instance in db_instances
                            if vpc_id == db_instance['DBSubnetGroup']['VpcId']]
    if db_names_and_subnets:
        db_name = db_names_and_subnets[0][0]
        try:
            response = rds_client.describe_db_instances(DBInstanceIdentifier=db_name)['DBInstances'][0]
            if 'VpcSecurityGroups' in response:
                db_security_groups = response['VpcSecurityGroups']
                if db_security_groups:
                    db_security_group_id = db_security_groups[0]['VpcSecurityGroupId']
                    response = ec2_client.describe_network_interfaces(
                        Filters=[
                            {
                                'Name': 'group-id',
                                'Values': [db_security_group_id]
                            }
                        ]
                    )
                    if response['NetworkInterfaces']:
                        network_interface_id = response['NetworkInterfaces'][0]['NetworkInterfaceId']
            else:
                return
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'DBInstanceNotFound':
                logging.error(f'Could not found the RDS, name: {db_name}')
                return

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

    if network_interface_id:
        try:
            network_interface_info = ec2_client.describe_network_interfaces(NetworkInterfaceIds=[network_interface_id])
            if 'NetworkInterfaces' in network_interface_info:
                if network_interface_info['NetworkInterfaces']:
                    if network_interface_info['NetworkInterfaces'][0]['Attachment']['Status'] == 'attached':
                        network_interface_attach_id = \
                            network_interface_info['NetworkInterfaces'][0]['Attachment']['AttachmentId']
                        ec2_client.detach_network_interface(
                            AttachmentId=network_interface_attach_id, Force=True
                        )
                        wait_for_network_interface_to_be_detached(ec2_client, network_interface_id)
                ec2_client.delete_network_interface(NetworkInterfaceId=network_interface_id)
                logging.info(f'Network interface {network_interface_id} is deleted.')
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'InvalidNetworkInterfaceID.NotFound':
                return


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
        delete_subnets(ec2_resource, vpc_id, aws_region)

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
    delete_hosted_zone_record_if_exists(aws_region, cluster_name)


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
            if "dynamic-pvc" in name or "nfs-shared-home" in name or "local-home" in name:
                logging.info(f"Volume {volume.id} is not in use and "
                             f"has 'dynamic-pvc', 'nfs-shared-home' or 'local-home' in name: deleting...")
                volumes.append(volume.id)

    logging.info(f"Found volumes: {volumes}")
    return volumes


def delete_ebs_volumes_by_id(aws_region, volumes):
    ec2 = boto3.resource('ec2', aws_region)

    # Terminate the volumes
    for volume_id in volumes:
        try:
            volume = ec2.Volume(volume_id)
            if volume.state == "in-use":
                logging.info(f"Volume {volume_id} is in use: skipping")
                continue
            volume.delete()
            logging.info(f"Terminated volume: {volume_id}")
        except Exception as e:
            logging.info(f"Failed to terminate volume {volume_id}: {e}")


def get_clusters_to_terminate():
    clusters_to_terminate = dict()
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
                clusters_to_terminate[rgn]=cluster
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
            logging.info("Skipping Alfred Open ID provider")
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
        logging.info(f"Open identity providers: {open_identities}")
    except Exception as e:
        logging.info(f"Failed to retrieve Open identity providers from {cluster_name}. Skipping...")
        logging.info(f"Error details: {e}")

    return open_identities


def delete_open_identities_for_cluster(open_identities):
    if not open_identities:
        logging.info("No OpenID Connect providers to delete.")
        return

    iam_client = boto3.client('iam')

    for identity in open_identities:
        try:
            providers = iam_client.list_open_id_connect_providers()['OpenIDConnectProviderList']
            for provider in providers:
                provider_identity_id = provider['Arn'].split('/id/')[-1]
                if provider_identity_id == identity:
                    iam_client.delete_open_id_connect_provider(OpenIDConnectProviderArn=provider['Arn'])
                    logging.info(f"Deleted identity provider: {identity}")
                else:
                    logging.info(f"Identity '{identity}' not found in provider '{provider['Arn']}'")
        except Exception as e:
            logging.info(f"Failed to delete identity provider: {identity}")
            logging.info(f"Error details: {e}")


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
        else:
            # mark roles without persist_days tag and created more than TTL for termination
            logging.warning(f"Role does NOT have 'persist_days' tag: {role['RoleName']}")
            max_role_ttl = 90     # days
            if datetime.now(role['CreateDate'].tzinfo) > role['CreateDate'] + timedelta(days=float(max_role_ttl)):
                logging.info(f"OLD role for TERMINATION: {role['RoleName']} was created "
                      f"{role['CreateDate']} > {max_role_ttl} days ago.")
                return True
    return False


def remove_iam_policy(policy_arn, policy_name):
    iam_client = boto3.client("iam")
    # list all versions of the policy
    r = iam_client.list_policy_versions(PolicyArn=policy_arn)
    for version in r['Versions']:
        if not version['IsDefaultVersion']:
            version_id = version['VersionId']
            iam_client.delete_policy_version(PolicyArn=policy_arn, VersionId=version_id)
            logging.info(f"Delete policy {policy_name} version: {version['VersionId']}")
    iam_client.delete_policy(PolicyArn=policy_arn)
    logging.info(f"Deleted policy {policy_name}")


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
            logging.info(f"Detached policy {policy['PolicyName']} from role {role_name}")

            if cluster_name in policy['PolicyName']:
                # Delete the policy
                remove_iam_policy(policy["PolicyArn"], policy['PolicyName'])

        # Delete the role
        iam_client.delete_role(RoleName=role_name)
        logging.info(f"Deleted Role: {role_name}")


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
        if (policy["PolicyName"].endswith("_Fleet-Enrollment") or
                policy["PolicyName"].endswith("_LaaS-policy") or
                policy["PolicyName"].endswith("_crowdstrike_s3") or
                policy["PolicyName"].endswith("_crowdstrike_secret")):
            remove_iam_policy(policy['PolicyArn'], policy["PolicyName"])
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


def delete_bucket_by_name(s3_client, bucket):
    objects_response = s3_client.list_objects_v2(Bucket=bucket)
    if 'Contents' in objects_response:
        objects = objects_response['Contents']
        for obj in objects:
            s3_client.delete_object(Bucket=bucket, Key=obj['Key'])
            logging.info(f"Object '{obj['Key']}' deleted successfully from bucket {bucket}.")
    versions = s3_client.list_object_versions(Bucket=bucket).get('Versions', [])
    delete_markers = s3_client.list_object_versions(Bucket=bucket).get('DeleteMarkers', [])
    if versions:
        for version in versions:
            s3_client.delete_object(Bucket=bucket, Key=version['Key'], VersionId=version['VersionId'])
            logging.info(f"S3 object version '{version}' deleted successfully from bucket {bucket}.")
    if delete_markers:
        for delete_marker in delete_markers:
            s3_client.delete_object(Bucket=bucket, Key=delete_marker['Key'], VersionId=delete_marker['VersionId'])
            logging.info(f"S3 delete marker '{delete_marker['Key']}' deleted successfully from bucket {bucket}.")
    try:
        s3_client.delete_bucket(Bucket=bucket)
        logging.info(f"S3 bucket '{bucket}' was successfully deleted.")
    except Exception as e:
        logging.warning(f"Could not delete s3 bucket '{bucket}': {e}")


def delete_s3_bucket_tf_state(cluster_name, aws_region):
    environment_name = retrieve_environment_name(cluster_name=cluster_name)
    s3_client = boto3.client('s3', region_name=aws_region)
    bucket_name_template = f'atl-dc-{environment_name}'
    response = s3_client.list_buckets()
    matching_buckets = [bucket['Name'] for bucket in response['Buckets'] if bucket_name_template in bucket['Name']]
    if not matching_buckets:
        logging.info(f"Could not find s3 bucket with name contains {bucket_name_template}")
        return
    for bucket in matching_buckets:
        delete_bucket_by_name(s3_client, bucket)


def delete_dynamo_bucket_tf_state(cluster_name, aws_region):
    environment_name = retrieve_environment_name(cluster_name=cluster_name)
    dynamodb_client = boto3.client('dynamodb', region_name=aws_region)
    dynamodb_name_template = f'atl_dc_{environment_name}'.replace('-', '_')
    response = dynamodb_client.list_tables()
    matching_tables = [table for table in response['TableNames'] if dynamodb_name_template in table]
    if not matching_tables:
        logging.info(f"Could not find dynamo db with name contains {dynamodb_name_template}")
        return
    for table in matching_tables:
        try:
            dynamodb_client.delete_table(TableName=table)
            logging.info(f"Dynamo db '{table}' was successfully deleted.")
        except Exception as e:
            logging.warning(f"Could not delete dynamo db '{table}': {e}")


def delete_expired_tf_state_s3_buckets():
    for rgn in REGIONS:
        logging.info(f"Region: {rgn}")
        s3_client = boto3.client('s3', region_name=rgn)
        bucket_name_template = f'atl-dc-'
        response = s3_client.list_buckets()
        if not response["Buckets"]:
            logging.info(f"There are no S3 buckets")
            return
        for bucket in response["Buckets"]:
            if bucket_name_template in bucket["Name"]:
                created_date = bucket["CreationDate"]
                tags = s3_client.get_bucket_tagging(Bucket=bucket["Name"])["TagSet"]
                persist_days = next((tag["Value"] for tag in tags if tag["Key"] == "persist_days"), None)
                if persist_days:
                    if not is_float(persist_days):
                        persist_days = 0
                    created_date_timestamp = created_date.timestamp()
                    persist_seconds = float(persist_days) * 24 * 60 * 60
                    now = time()
                    if created_date_timestamp + persist_seconds > now:
                        logging.info(f"S3 bucket {bucket['Name']} is not EOL yet, skipping...")
                    else:
                        logging.info(f"S3 bucket {bucket['Name']} is EOL and should be deleted.")
                        delete_bucket_by_name(s3_client, bucket['Name'])
                else:
                    logging.warning(f"S3 bucket {bucket['Name']} does not have tags.")


def is_policy_attached(policy_arn):
    iam_client = boto3.client("iam")
    r = iam_client.list_entities_for_policy(PolicyArn=policy_arn)
    policy_users = r['PolicyUsers']
    policy_groups = r['PolicyGroups']
    policy_roles = r['PolicyRoles']
    if policy_users or policy_groups or policy_roles:
        return True
    else:
        return False


def delete_expired_iam_policies():
    iam_client = boto3.client("iam")
    finished = False
    marker = None
    policies = list()
    while not finished:
        if marker:
            policies_batch = iam_client.list_policies(MaxItems=1000, Scope="Local", Marker=marker)
        else:
            policies_batch = iam_client.list_policies(MaxItems=1000, Scope="Local")
        policies.extend(policies_batch["Policies"])
        if policies_batch['IsTruncated']:
            marker = policies_batch['Marker']
        else:
            finished = True
    for policy in policies:
        if policy['PolicyName'].startswith('atlas-'):
            # skip attached policies
            if is_policy_attached(policy['Arn']):
                logging.warning(f"Policy {policy['PolicyName']} is attached. Skipping termination.")
                continue

            tags = iam_client.list_policy_tags(PolicyArn=policy['Arn'])
            persist_days = None

            # delete all expired policies
            for tag in tags["Tags"]:
                if tag["Key"] == "persist_days":
                    try:
                        persist_days = float(tag["Value"])
                    except ValueError:
                        ...
            if persist_days:
                eol_time = policy['CreateDate'] + timedelta(days=float(persist_days))
                if datetime.now(policy['CreateDate'].tzinfo) > eol_time:
                    logging.info(f"Policy expired {policy['PolicyName']}: "
                                 f"create date {policy['CreateDate']}, persist_days: {persist_days}")

                    remove_iam_policy(policy['Arn'], policy['PolicyName'])
                else:
                    logging.info(f"Policy is NOT expired {policy['PolicyName']}: "
                                 f"create date {policy['CreateDate']}, persist_days: {persist_days}")
            else:
                # Delete policies without persist_days tag and created more that max policy TTL
                max_policy_ttl = 90     # days
                logging.warning(f"Policy does NOT have 'persist_days' tag: {policy['PolicyName']}. "
                                f"Creation date: {policy['CreateDate']}")
                create_date = datetime.now(policy['CreateDate'].tzinfo)
                if create_date > policy['CreateDate'] + timedelta(days=float(max_policy_ttl)):
                    logging.info(f"Policy {policy['PolicyName']} was created "
                                 f"{policy['CreateDate']} > {max_policy_ttl} days ago.")
                    remove_iam_policy(policy['Arn'], policy['PolicyName'])


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
        delete_s3_bucket_tf_state(cluster_name=args.cluster_name, aws_region=args.aws_region)
        delete_dynamo_bucket_tf_state(cluster_name=args.cluster_name, aws_region=args.aws_region)
        return

    logging.info("--cluster_name parameter was not specified.")
    logging.info("Searching for clusters to remove.")
    clusters = get_clusters_to_terminate()
    for region, cluster_name in clusters.items():
        logging.info(f"Delete all resources and VPC for cluster {cluster_name}.")
        terminate_cluster(cluster_name=cluster_name)
        vpc_name = f'{cluster_name.replace("-cluster", "-vpc")}'
        terminate_vpc(vpc_name=vpc_name)
        terminate_open_id_providers(cluster_name=cluster_name)
        delete_s3_bucket_tf_state(cluster_name=cluster_name, aws_region=region)
        delete_dynamo_bucket_tf_state(cluster_name=cluster_name, aws_region=region)
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
    delete_expired_iam_policies()
    logging.info("Terminate unused and expired ebs volumes")
    delete_unused_volumes()
    logging.info("Search for abandoned S3 buckets")
    delete_expired_tf_state_s3_buckets()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
