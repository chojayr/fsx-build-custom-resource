from __future__ import print_function
from crhelper import CfnResource
import logging
import os 
import sys
import base64
import time
import boto3

logger = logging.getLogger(__name__)
# Initialise the helper, all inputs are optional, this example shows the defaults
helper = CfnResource(json_logging=False, log_level='DEBUG', boto_level='CRITICAL')

client = boto3.client('fsx')
kms_client = boto3.client('kms')


@helper.create
def create(event, context):

    logger.info("Got Create")

    storage_capacity, subnet_id, security_group1, security_group2, security_group3, name, team, service, kmskey, domain_name, fs_admin, ou_name, username, password, dnsip1, dnsip2, throughput = _get_resource_properties(event)

    encrypted_pass = base64.b64decode(password)
    decrypt_password = _decrypt_pass(encrypted_pass)

    physical_id = _create(storage_capacity, subnet_id, security_group1, security_group2, security_group3, name, team, service, kmskey, domain_name, fs_admin, ou_name, username, decrypt_password, dnsip1, dnsip2, throughput)

    return physical_id


@helper.update
def update(event, context):
    logger.info("Got Update")
    # If the update resulted in a new resource being created, return an id for the new resource. CloudFormation will send
    # a delete event with the old id when stack update completes


@helper.delete
def delete(event, context):
    logger.info("Start to Delete")
    print(event)

    fsx_id = _get_physical_id(event)
    return _delete(fsx_id)


@helper.poll_create
def poll_create(event, context):
    logger.info("Got create poll")
    # Return a resource id or True to indicate that creation is complete. if True is returned an id will be generated
    fsx_id = _get_crhelper_data(event)

    poll_result = _polling(fsx_id)
    if poll_result == False:
        return poll_result
    else: 
        return poll_result


def handler(event, context):
    helper(event, context)

def _get_resource_properties(event):

    properties = event.get('ResourceProperties', None)

    storage_capacity = properties.get('StorageCapacity')
    subnet_id = properties.get('SubnetId')
    security_group1 = properties.get('SecurityGroupId1')
    security_group2 = properties.get('SecurityGroupId2')
    security_group3 = properties.get('SecurityGroupId3')
    name = properties.get('FSName')
    team = properties.get('Team')
    service = properties.get('Service')
    kmskey = properties.get('KmsKey')
    domain_name = properties.get('DomainName')
    fs_admin = properties.get('FSAdminGroup')
    ou_name = properties.get('OrganizationalUnitName')
    username = properties.get('UserName')
    password = properties.get('Password')
    dnsip1 = properties.get('DNSIp1')
    dnsip2 = properties.get('DNSIp2')
    throughput = properties.get('ThroughputCapacity')

    return storage_capacity, subnet_id, security_group1, security_group2, security_group3, name, team, service, kmskey, domain_name, fs_admin, ou_name, username, password, dnsip1, dnsip2, throughput


def _get_crhelper_data(event):

    helper_data = event.get('CrHelperData', None)
    physical_id = helper_data.get('PhysicalResourceId')

    return physical_id


def _get_physical_id(event):

    event_data = event.get('PhysicalResourceId')

    return event_data


def _decrypt_pass(encrypted_pass):
    try:
        response = kms_client.decrypt(
                CiphertextBlob=encrypted_pass
        )
        decrypt_result = response["Plaintext"]
        decoded_string = decrypt_result.decode("utf-8")
        return decoded_string
    except Exception as err:
        logger.error(err)


def _create(storage_capacity, subnet_id, security_group1, security_group2, security_group3, name, team, service, kmskey, domain_name, fs_admin, ou_name, username, decrypt_password, dnsip1, dnsip2, throughput):

    storage_capacity_int = int(storage_capacity)
    throughput_int = int(throughput)

    if not storage_capacity_int:
        raise Exception('Must provide a "StorageCapacity" value in properties.')
    elif storage_capacity_int < 300:
        raise Exception('StorageCapacity value should be 300 or above')
    
    response = client.create_file_system(
            FileSystemType='WINDOWS',
            StorageCapacity=storage_capacity_int,
            SubnetIds=[
                subnet_id,
            ],
            SecurityGroupIds=[
                security_group1,
                security_group2,
                security_group3
            ],
            Tags=[
                {
                    'Key': 'Name',
                    'Value': name
                },
                {
                    'Key': 'Team',
                    'Value': team
                },
                {
                    'Key': 'Service',
                    'Value': service
                }
            ],
            KmsKeyId=kmskey,
            WindowsConfiguration={
                'SelfManagedActiveDirectoryConfiguration': {
                    'DomainName': domain_name,
                    'OrganizationalUnitDistinguishedName': ou_name,
                    'FileSystemAdministratorsGroup': fs_admin,
                    'UserName': username,
                    'Password': decrypt_password,
                    'DnsIps': [ 
                        dnsip1,
                        dnsip2
                    ]
                },
                'ThroughputCapacity': throughput_int,
                'CopyTagsToBackups': True
            }
    )

    fsx_id = response["FileSystem"]["FileSystemId"]

    helper.Data.update({"filesystemid": fsx_id})
    helper.PhysicalResourceId = fsx_id

    return fsx_id



def _polling(fsx_id):

    poll_response = client.describe_file_systems(
            FileSystemIds=[
                fsx_id,
            ]
    )
    for fsx_status in poll_response["FileSystems"]:
        status = fsx_status["Lifecycle"]
        if status == "CREATING":
            return False
        elif status == "AVAILABLE":
            helper.PhysicalResourceId = fsx_id
            return fsx_id


def _delete(fsx_id):

    try:
        delete_response = client.delete_file_system(
            FileSystemId=fsx_id,
            WindowsConfiguration={
                'SkipFinalBackup': True
            }
        )
        logger.info("Delete resource")
        return delete_response
    except Exception as e:
        logger.error(e)

