import boto3
from botocore.exceptions import ClientError
import csv
import traceback

# Initialize the RAM client
ram_client = boto3.client('ram')

# List of AWS resource types that cannot be shared outside the organization
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
        print(traceback.format_exc())
        return []
    except Exception as e:
        print("Unexpected error in list_ram_resource_shares:")
        print(traceback.format_exc())
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
        print(traceback.format_exc())
        return []
    except Exception as e:
        print("Unexpected error in list_resources_in_share:")
        print(traceback.format_exc())
        return []

def check_for_non_shareable_resources(output_directory):
    """Check if any resource shares with resource owner as SELF/OTHER-ACCOUNTS include resources that are in the NON_SHAREABLE_RESOURCE_TYPES list."""
    try:
        resource_shares_self = list_ram_resource_shares(resource_owner='SELF')
        resource_shares_other_accounts = list_ram_resource_shares(resource_owner='OTHER-ACCOUNTS')

        # if not resource_shares_self and not resource_shares_other_accounts:
        #     print("No active resource shares found!")
        #     return
        if resource_shares_self or resource_shares_other_accounts:
        # Exporting data to CSV as resource share is found
            print("Resource Shares found")
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

                # Check if any resource shares with resource owner as OTHER-ACCOUNTS include resources that are in the NON_SHAREABLE_RESOURCE_TYPES list.
                for share in resource_shares_other_accounts:
                    resource_share_arn = share['resourceShareArn']
                    resources = list_resources_in_share(resource_share_arn, resource_owner='OTHER-ACCOUNTS')

                    for resource in resources:
                        resource_type = resource['type']
                        resource_arn = resource['arn']

                        if resource_type in NON_SHAREABLE_RESOURCE_TYPES:
                            writer.writerow([resource_type, resource_arn, 'Yes'])
                        else:
                            writer.writerow([resource_type, resource_arn, 'No'])
        else:
            print("No Resource shares active")

    except Exception as e:
        print("Unexpected error in check_for_non_shareable_resources:")
        print(traceback.format_exc())

if __name__ == "__main__":
    try:
        check_for_non_shareable_resources('testorg')
    except Exception as e:
        print("Error in the main program:")
        print(traceback.format_exc())
