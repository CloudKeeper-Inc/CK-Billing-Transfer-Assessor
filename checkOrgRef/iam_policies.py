import boto3
import re


def get_customer_managed_policies(iam_client):
    """Retrieve a list of all customer-managed IAM policies."""
    policies = []
    paginator = iam_client.get_paginator('list_policies')
    for page in paginator.paginate(Scope='Local'):
        policies.extend(page['Policies'])
    return policies

def get_policy_document(iam_client,policy_arn, version_id):
    """Retrieve the policy document for a specific version of a policy."""
    response = iam_client.get_policy_version(
        PolicyArn=policy_arn,
        VersionId=version_id
    )
    return response['PolicyVersion']['Document']

def check_policy_for_org_id(policy_document,org_id_pattern):
    """Check if the policy document contains an org ID or 'PrincipalOrgID'."""
    policy_str = str(policy_document)
    if 'PrincipalOrgID' in policy_str or org_id_pattern.search(policy_str):
        return True
    return False

def check_iam_policies(org_id_pattern):
    iam_client = boto3.client('iam')
    print("Fetching customer-managed IAM policies...")
    policies = get_customer_managed_policies(iam_client)
    flagged_policies = []

    print(f"Found {len(policies)} customer-managed policies. Checking for organization IDs...")
    for policy in policies:
        policy_arn = policy['Arn']
        default_version_id = policy['DefaultVersionId']
        policy_document = get_policy_document(iam_client,policy_arn, default_version_id)
        
        if check_policy_for_org_id(policy_document,org_id_pattern):
            flagged_policies.append(policy_arn)

    if flagged_policies:
        print("Policies containing organization IDs or 'PrincipalOrgID':")
        for policy_arn in flagged_policies:
            print(f"- {policy_arn}")
    else:
        print("No policies containing organization IDs or 'PrincipalOrgID' were found.")

def main():

    org_id_pattern = re.compile(r'\bo-[a-zA-Z0-9]{4,32}\b')
    check_iam_policies(org_id_pattern)


if __name__ == "__main__":
    main()
