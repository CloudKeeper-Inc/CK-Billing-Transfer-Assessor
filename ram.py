import boto3
from botocore.exceptions import ClientError
import csv

# Initialize the RAM client
ram_client = boto3.client('ram')

'''List of AWS resource types that cannot be shared outside the organization
   This has been obtained from https://docs.aws.amazon.com/ram/latest/userguide/shareable.html'''

NON_SHAREABLE_RESOURCE_TYPES = [
    "bedrock:CustomModel",
    "outposts:Outpost",
    "ec2:LocalGatewayRouteTable",
    "s3-outposts:Outpost",
    "resource-explorer-2:View",
    "servicecatalog:Application",
    "servicecatalog:AttributeGroup",
    "ec2:CoipPool",
    "ec2:Subnet",
]

def list_ram_resource_shares(resource_owner):
    """List all active resource shares."""
    try:
        response = ram_client.get_resource_shares(
            resourceOwner=resource_owner,  # Resources owned by your account
            resourceShareStatus='ACTIVE'
        )
        return response['resourceShares']
    except ClientError as e:
        print(f"Error fetching resource shares: {e}")
        return []

def list_resources_in_share(resource_share_arn, resource_owner):
    """List all resources in a given resource share."""
    try:
        response = ram_client.list_resources(
            resourceOwner=resource_owner,
            resourceShareArns=[resource_share_arn]
        )
        return response['resources']
    except ClientError as e:
        print(f"Error fetching resources for resource share {resource_share_arn}: {e}")
        return []

def check_for_non_shareable_resources(output_directory):
    """Check if any resource shares with resource owner as SELF/OTHER-ACCOUNTS include resources that are in the NON_SHAREABLE_RESOURCE_TYPES list."""
    resource_shares_self = list_ram_resource_shares(resource_owner='SELF')
    resource_shares_other_accounts = list_ram_resource_shares(resource_owner='OTHER-ACCOUNTS')

    if not resource_shares_self and not resource_shares_other_accounts:
        print("No active resource shares found !")
        return
    
    """Exporting data to CSV as resource share is found"""
    header = ['Resource Type', 'Resource ARN', 'ORG Dependency']
    with open(f'{output_directory}/RAM.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(header)

        for share in resource_shares_self:
            resource_share_arn = share['resourceShareArn']
            resources = list_resources_in_share(resource_share_arn, resource_owner='SELF')

            for resource in resources:
                resource_type = resource['type']
                resource_arn = resource['arn']

                if resource_type in NON_SHAREABLE_RESOURCE_TYPES:
                    writer.writerow([resource_type, resource_arn, 'Yes'])
                else:
                    writer.writerow([resource_type, resource_arn, 'No'])

        
        """Check if any resource shares with resource owner as OTHER-ACCOUNTS include resources that are in the NON_SHAREABLE_RESOURCE_TYPES list."""

        for share in resource_shares_other_accounts:
            resource_share_arn = share['resourceShareArn']
            resources = list_resources_in_share(resource_share_arn, resource_owner='OTHER-ACCOUNTS')

            for resource in resources:
                resource_type = resource['type']
                resource_arn = resource['arn']

                if resource_type in NON_SHAREABLE_RESOURCE_TYPES:
                    # print(f"WARNING: Resource of type '{resource_type}' (ARN: {resource_arn}) "
                    #     f"is being shared and can not be shared outside your organization.")
                    writer.writerow([resource_type, resource_arn, 'Yes'])
                else:
                    # print(f"Resource of type '{resource_type}' (ARN: {resource_arn}) is shareable outside organization.")
                    writer.writerow([resource_type, resource_arn, 'No'])
        

    

if __name__ == "__main__":
    check_for_non_shareable_resources('testorg')
