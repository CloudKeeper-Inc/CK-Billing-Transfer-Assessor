import boto3
import traceback

# List of all AWS regions
def get_all_regions():
    try:
        ec2_client = boto3.client('ec2')
        response = ec2_client.describe_regions()
        return [region['RegionName'] for region in response['Regions']]
    except Exception as e:
        print("Error in get_all_regions:")
        print(traceback.format_exc())
        raise  # Re-raise the exception after logging it

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
        # Print the detailed traceback if the API call fails
        print(f"Error checking SSO in region {region}:")
        print(traceback.format_exc())
        return False

def find_region_with_sso():
    try:
        regions = get_all_regions()
        for region in regions:
            if check_sso_enabled_in_region(region):
                print(f"SSO is enabled in region: {region}")
                return region
        print("SSO is not enabled in any region.")
        return None
    except Exception as e:
        print("Error in find_region_with_sso:")
        print(traceback.format_exc())
        raise  # Re-raise the exception after logging it

if __name__ == "__main__":
    try:
        region_with_sso = find_region_with_sso()
        if region_with_sso:
            print(f"SSO is enabled in: {region_with_sso}")
        else:
            print("No region has SSO enabled.")
    except Exception as e:
        print("An error occurred in the main program:")
        print(traceback.format_exc())
