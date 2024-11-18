import boto3
import re



def check_organization_references_in_sns_policy(region,org_id_pattern):
    try:
        sns_client = boto3.client('sns',region_name =region)
        topics_response = sns_client.list_topics()
        topics = topics_response.get('Topics', [])

        for topic in topics:
            topic_arn = topic['TopicArn']

            try:
                attributes = sns_client.get_topic_attributes(TopicArn=topic_arn)
                policy = attributes['Attributes'].get('Policy', '')

                org_id_found = org_id_pattern.search(policy)

                principal_org_id_found = "PrincipalOrgID" in policy

                if org_id_found or principal_org_id_found:
                    print(f"Organization ID reference found in policy for topic: {topic_arn}")

            except Exception as e:
                print(f"An error occurred while checking the policy for topic {topic_arn}: {str(e)}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")



def main():
    region = sys.argv[1]
    org_id_pattern = re.compile(r'\bo-[a-zA-Z0-9]{4,32}\b')
    check_organization_references_in_sns_policy(region,org_id_pattern)

