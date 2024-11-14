import boto3
import re
import json

# Regular expression to match organization IDs
org_id_pattern = re.compile(r'\bo-[a-zA-Z0-9]{4,32}\b')

# Initialize EC2 client
ec2_client = boto3.client('ec2')

def get_vpc_endpoints():
    """Retrieve a list of all VPC endpoints."""
    endpoints = []
    paginator = ec2_client.get_paginator('describe_vpc_endpoints')
    for page in paginator.paginate():
        endpoints.extend(page['VpcEndpoints'])
    return endpoints

def check_policy_for_org_id(policy_document):
    """Check if the policy document contains an org ID or 'PrincipalOrgID'."""
    policy_str = json.dumps(policy_document)  # Convert policy document to a JSON string
    if 'PrincipalOrgID' in policy_str or org_id_pattern.search(policy_str):
        return True
    return False

def main():
    print("Fetching VPC endpoints...")
    endpoints = get_vpc_endpoints()
    flagged_endpoints = []

    print(f"Found {len(endpoints)} VPC endpoints. Checking for organization IDs...")
    for endpoint in endpoints:
        endpoint_id = endpoint['VpcEndpointId']
        policy_document = endpoint.get('PolicyDocument')  # VPC endpoint policy

        if policy_document and check_policy_for_org_id(policy_document):
            flagged_endpoints.append(endpoint_id)

    if flagged_endpoints:
        print("VPC endpoints containing organization IDs or 'PrincipalOrgID' in policies:")
        for endpoint_id in flagged_endpoints:
            print(f"- {endpoint_id}")
    else:
        print("No VPC endpoints containing organization IDs or 'PrincipalOrgID' in policies were found.")

if __name__ == "__main__":
    main()
