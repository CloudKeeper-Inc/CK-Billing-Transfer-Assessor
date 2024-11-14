import boto3
import re
import json
from botocore.exceptions import ClientError

# Regular expression to match organization IDs
org_id_pattern = re.compile(r'\bo-[a-zA-Z0-9]{4,32}\b')

# Initialize S3 client
s3_client = boto3.client('s3')

def get_all_buckets():
    """Retrieve a list of all S3 buckets."""
    response = s3_client.list_buckets()
    return [bucket['Name'] for bucket in response['Buckets']]

def get_bucket_region(bucket_name):
    """Retrieve the region of a specific S3 bucket."""
    response = s3_client.get_bucket_location(Bucket=bucket_name)
    return response['LocationConstraint'] or 'us-east-1'  # Default to us-east-1 if None

def get_bucket_policy(bucket_name, region):
    """Retrieve the policy document for a specific S3 bucket in the correct region."""
    regional_s3_client = boto3.client('s3', region_name=region)  # Use a regional client
    try:
        response = regional_s3_client.get_bucket_policy(Bucket=bucket_name)
        return json.loads(response['Policy'])  # Return the policy document as JSON
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
            return None  # No policy exists for this bucket
        else:
            raise  # Reraise other exceptions

def check_policy_for_org_id(policy_document):
    """Check if the policy document contains an org ID or 'PrincipalOrgID'."""
    policy_str = json.dumps(policy_document)  # Convert policy document to a JSON string
    return 'PrincipalOrgID' in policy_str or org_id_pattern.search(policy_str)

def main():
    print("Fetching all S3 buckets...")
    buckets = get_all_buckets()
    flagged_buckets = []

    print(f"Found {len(buckets)} buckets. Checking for organization IDs in bucket policies...")
    for bucket_name in buckets:
        try:
            region = get_bucket_region(bucket_name)  # Get the region of the bucket
            policy_document = get_bucket_policy(bucket_name, region)  # Get the policy using the correct region

            if policy_document and check_policy_for_org_id(policy_document):
                flagged_buckets.append(bucket_name)

        except ClientError as e:
            print(f"Error processing bucket {bucket_name}: {e}")

    if flagged_buckets:
        print("Buckets containing organization IDs or 'PrincipalOrgID' in policies:")
        for bucket_name in flagged_buckets:
            print(f"- {bucket_name}")
    else:
        print("No buckets containing organization IDs or 'PrincipalOrgID' in policies were found.")

if __name__ == "__main__":
    main()
