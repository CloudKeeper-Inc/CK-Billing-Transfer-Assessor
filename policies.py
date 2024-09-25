import boto3
import csv
import os
import json
import traceback

def get_scp_policies(client):
    try:
        # Get SCP policies from AWS Organizations
        scp_policies = []
        paginator = client.get_paginator('list_policies')
        for page in paginator.paginate(Filter='SERVICE_CONTROL_POLICY'):
            scp_policies.extend(page['Policies'])
        return scp_policies
    except Exception as e:
        print("Error in get_scp_policies:")
        print(traceback.format_exc())
        raise

def get_backup_policies(client):
    try:
        # Get Backup policies from AWS Organizations
        backup_policies = []
        paginator = client.get_paginator('list_policies')
        for page in paginator.paginate(Filter='BACKUP_POLICY'):
            backup_policies.extend(page['Policies'])
        return backup_policies
    except Exception as e:
        print("Error in get_backup_policies:")
        print(traceback.format_exc())
        raise

def get_tag_policies(client):
    try:
        # AWS Organizations Tag Policies (requires Organizations client)
        tag_policies = []
        paginator = client.get_paginator('list_policies')
        for page in paginator.paginate(Filter='TAG_POLICY'):
            tag_policies.extend(page['Policies'])
        return tag_policies
    except Exception as e:
        print("Error in get_tag_policies:")
        print(traceback.format_exc())
        raise

def get_policy_targets(client, policy_id):
    try:
        # Get the targets (accounts, OUs, root) that the policy is attached to
        targets = []
        paginator = client.get_paginator('list_targets_for_policy')
        for page in paginator.paginate(PolicyId=policy_id):
            targets.extend(page['Targets'])
        
        # Extract relevant details (target type and ID)
        target_details = []

        if not targets:
            target_details.append("None")
            return ', '.join(target_details)
        
        for target in targets:
            target_details.append(f"{target['Type']} - {target['TargetId']}")
        
        return ', '.join(target_details)
    except Exception as e:
        print(f"Error in get_policy_targets for policy {policy_id}:")
        print(traceback.format_exc())
        raise

def get_policy_content(client, policy_id):
    try:
        # Get the content (document) of the policy
        response = client.describe_policy(PolicyId=policy_id)
        policy_content = response['Policy']['Content']
        return policy_content
    except Exception as e:
        print(f"Error in get_policy_content for policy {policy_id}:")
        print(traceback.format_exc())
        raise

def save_policy_content_to_json(policy_name, policy_type, policy_content, output_directory):
    try:
        # Ensure the policy content directory exists
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        # Construct the filename using the policy name and type
        file_name = f"{policy_type}_{policy_name}.json"
        sanitized_name = file_name.replace(' ', '_')  # Replace spaces with underscores
        file_path = os.path.join(output_directory, sanitized_name)

        # Write the policy content to a JSON file
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(json.loads(policy_content), json_file, indent=4)
    except Exception as e:
        print(f"Error in save_policy_content_to_json for policy {policy_name}:")
        print(traceback.format_exc())
        raise

def write_policies_to_csv(client, policies, file_name, policy_type, output_dir):
    try:
        # Open the CSV file for writing
        with open(file_name, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            # Write the policy data with targets and save content to JSON
            for policy in policies:
                policy_id = policy['Id']
                policy_name = policy['Name']
                description = policy.get('Description', '')
                
                # Get the policy targets
                targets = get_policy_targets(client, policy_id)
                
                # Get the policy content
                policy_content = get_policy_content(client, policy_id)
                
                # Save the policy content to a JSON file
                save_policy_content_to_json(policy_name, policy_type, policy_content, output_dir)
                
                # Write policy details and targets to CSV
                writer.writerow([policy_id, policy_name, description, policy_type, targets])
    except Exception as e:
        print(f"Error in write_policies_to_csv for {policy_type} policies:")
        print(traceback.format_exc())
        raise

def get_policies(client, outputDirectory, policyContentDirectory):
    try:
        # Write the header with targets and policy content
        header = ['Policy ID', 'Policy Name', 'Description', 'Policy Type', 'Targets']
        with open(f'{outputDirectory}/policies.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(header)

        # Step 1: Get SCP policies
        print("Fetching SCP policies if any...")
        scp_policies = get_scp_policies(client)
        write_policies_to_csv(client, scp_policies, f'{outputDirectory}/policies.csv', 'SCP', policyContentDirectory)

        # Step 2: Get Backup policies
        print("Fetching Backup policies if any...")
        backup_policies = get_backup_policies(client)
        write_policies_to_csv(client, backup_policies, f'{outputDirectory}/policies.csv', 'Backup', policyContentDirectory)

        # Step 3: Get Tag policies
        print("Fetching Tag policies if any...")
        tag_policies = get_tag_policies(client)
        write_policies_to_csv(client, tag_policies, f'{outputDirectory}/policies.csv', 'Tag Policy', policyContentDirectory)

        print("CSV files and policy JSON files generated successfully.")
    except Exception as e:
        print("Error in get_policies:")
        print(traceback.format_exc())
        raise

if __name__ == '__main__':
    try:
        # Initialize boto3 client for AWS Organizations
        client = boto3.client('organizations')

        # Specify the output directory for the CSV
        output_dir = './'

        # Specify the directory where policy contents will be saved as JSON
        policy_content_dir = './policy_content'
        
        # Get the policies and export them to a CSV and JSON
        get_policies(client, output_dir, policy_content_dir)
    except Exception as e:
        print("Error in the main program:")
        print(traceback.format_exc())
