import boto3
import re

# Initialize the ECR client
ecr_client = boto3.client('ecr')

# Regular expression pattern to match an AWS Organization ID (e.g., o-xxxxxxx)
org_id_pattern = re.compile(r'\bo-[a-zA-Z0-9]{4,32}\b')  # Adjust length as needed based on org ID format

def check_organization_references_in_policy():
    try:
        # Get all ECR repositories
        repos = ecr_client.describe_repositories()['repositories']
        
        for repo in repos:
            repo_name = repo['repositoryName']
            print(f"Checking policy for repository: {repo_name}")
            
            try:
                # Get the repository policy
                policy = ecr_client.get_repository_policy(repositoryName=repo_name)['policyText']
                
                # Check for any organization ID pattern
                org_id_found = org_id_pattern.search(policy)
                
                # Check specifically for the text "PrincipalOrgID"
                principal_org_id_found = "PrincipalOrgID" in policy
                
                # Output results based on findings
                if org_id_found or principal_org_id_found:
                    print(f"Organization ID reference found in policy for repository: {repo_name}")
                    if org_id_found:
                        print("Generic Organization ID found")
                    if principal_org_id_found:
                        print("PrincipalOrgID found in policy")
                    print(policy)  # Print policy for further inspection
                else:
                    print(f"No organization ID reference found in policy for repository: {repo_name}")
                    
            except ecr_client.exceptions.RepositoryPolicyNotFoundException:
                print(f"No policy found for repository: {repo_name}")
                
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Run the function
check_organization_references_in_policy()
