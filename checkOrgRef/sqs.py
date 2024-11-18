import boto3
import re


def check_organization_references_in_sqs_policy(region,org_id_pattern):
    try:
        sqs_client = boto3.client('sqs', region_name=region)
        # Get the list of all SQS queue URLs
        queues_response = sqs_client.list_queues()
        queue_urls = queues_response.get('QueueUrls', [])

        for queue_url in queue_urls:
            print(f"Checking policy for queue: {queue_url}")

            try:
                # Get the queue attributes, including the policy
                attributes = sqs_client.get_queue_attributes(
                    QueueUrl=queue_url,
                    AttributeNames=['Policy']
                )
                policy = attributes.get('Attributes', {}).get('Policy', '')

                # Check for any organization ID pattern
                org_id_found = org_id_pattern.search(policy)

                # Check specifically for the text "PrincipalOrgID"
                principal_org_id_found = "PrincipalOrgID" in policy

                # Output results based on findings
                if org_id_found or principal_org_id_found:
                    print(f"Organization ID reference found in policy for queue: {queue_url}")
                

            except Exception as e:
                print(f"An error occurred while checking the policy for queue {queue_url}: {str(e)}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")



def main():
    region = sys.argv[1]
    org_id_pattern = re.compile(r'\bo-[a-zA-Z0-9]{4,32}\b')
    check_organization_references_in_sqs_policy(region,org_id_pattern)

