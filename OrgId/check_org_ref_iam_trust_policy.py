import boto3
import re

# Regular expression to match organization IDs
org_id_pattern = re.compile(r'\bo-[a-zA-Z0-9]{4,32}\b')

# Initialize IAM client
iam_client = boto3.client('iam')

def get_customer_managed_roles():
    """Retrieve a list of all customer-managed IAM roles."""
    roles = []
    paginator = iam_client.get_paginator('list_roles')
    for page in paginator.paginate():
        for role in page['Roles']:
            # Include only roles that are customer-managed (exclude AWS-managed roles)
            if not role['Arn'].startswith('arn:aws:iam::aws:role/'):
                roles.append(role)
    return roles

def get_trust_policy(role_name):
    """Retrieve the trust relationship policy for a specific role."""
    response = iam_client.get_role(RoleName=role_name)
    return response['Role']['AssumeRolePolicyDocument']

def check_trust_policy_for_org_id(trust_policy):
    """Check if the trust policy contains an org ID or 'PrincipalOrgID'."""
    policy_str = str(trust_policy)
    if 'PrincipalOrgID' in policy_str or org_id_pattern.search(policy_str):
        return True
    return False

def main():
    print("Fetching customer-managed IAM roles...")
    roles = get_customer_managed_roles()
    flagged_roles = []

    print(f"Found {len(roles)} customer-managed roles. Checking for organization IDs...")
    for role in roles:
        role_name = role['RoleName']
        trust_policy = get_trust_policy(role_name)
        
        if check_trust_policy_for_org_id(trust_policy):
            flagged_roles.append(role['Arn'])

    if flagged_roles:
        print("Roles containing organization IDs or 'PrincipalOrgID' in trust policies:")
        for role_arn in flagged_roles:
            print(f"- {role_arn}")
    else:
        print("No roles containing organization IDs or 'PrincipalOrgID' in trust policies were found.")

if __name__ == "__main__":
    main()
