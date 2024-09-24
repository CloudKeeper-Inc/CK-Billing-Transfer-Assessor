import boto3

# List of all AWS regions
def get_all_regions():
    ec2_client = boto3.client('ec2')
    response = ec2_client.describe_regions()
    return [region['RegionName'] for region in response['Regions']]

# Check if SSO is enabled in the given region
def check_sso_enabled_in_region(region):
    try:
        # Initialize the SSO client for the specified region
        sso_client = boto3.client('sso-admin', region_name=region)
        
        # Attempt to list SSO instances (this will work only if SSO is enabled in the region)
        response = sso_client.list_instances()
        if response['Instances']:
            return True
        return False
    
    except Exception as e:
        # If the API call fails, SSO is likely not enabled in this region
        return False

def find_region_with_sso():
    regions = get_all_regions()
    for region in regions:
        if check_sso_enabled_in_region(region):
            print(f"SSO is enabled in region: {region}")
            return region
    print("SSO is not enabled in any region.")
    return None