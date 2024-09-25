import csv
import os
import boto3
import traceback

rootAccountId = ''  # Can be avoided if not used elsewhere

def get_aws_accounts(client):
    """Retrieve all AWS accounts in the organization."""
    try:
        accounts = []
        paginator = client.get_paginator('list_accounts')
        for page in paginator.paginate():
            accounts.extend(page['Accounts'])
        return accounts
    except Exception as e:
        print("Error while fetching AWS accounts:")
        traceback.print_exc()
        return []

def identify_root_account(client):
    """Identify and return the root account ID of the organization."""
    try:
        response = client.describe_organization()
        organization = response['Organization']
        root_account_id = organization['MasterAccountId']
        return root_account_id
    except client.exceptions.AWSOrganizationsNotInUseException:
        print("AWS Organizations is not enabled in this account.")
        traceback.print_exc()
    except Exception as e:
        print("Error while identifying root account:")
        traceback.print_exc()
    return None

def write_accounts_to_csv(accounts, root_account_id, file_name):
    """Write AWS account details to a CSV file."""
    try:
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        
        # Define the header for the CSV file
        header = ['Account ID', 'Account Name', 'Email', 'Status', 'Root Account']

        # Open the CSV file for writing
        with open(file_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            
            # Write the header
            writer.writerow(header)
            
            # Write the account data
            for account in accounts:
                is_root = 'Yes' if account['Id'] == root_account_id else '-'
                writer.writerow([account['Id'], account['Name'], account['Email'], account['Status'], is_root])
        
        print(f"CSV file written successfully at {file_name}")

    except FileNotFoundError as fnf_error:
        print(f"File not found error: {fnf_error}")
        traceback.print_exc()
    except IOError as io_error:
        print(f"IO error while writing CSV: {io_error}")
        traceback.print_exc()
    except Exception as e:
        print("An unexpected error occurred while writing to CSV:")
        traceback.print_exc()

def get_account_details(client, output_directory):
    """Main function to fetch accounts and write them to a CSV file."""
    try:
        # Step 1: Get AWS accounts and root account
        print("Fetching AWS accounts...")
        accounts = get_aws_accounts(client)
        if not accounts:
            print("No accounts retrieved. Exiting.")
            return
        
        root_account_id = identify_root_account(client)
        if root_account_id is None:
            print("Unable to identify the root account. Exiting.")
            return

        # Step 2: Write AWS accounts to CSV
        print("Writing AWS accounts to CSV...")
        write_accounts_to_csv(accounts, root_account_id, f'{output_directory}/aws_accounts.csv')
        
    except NoCredentialsError:
        print("AWS credentials not found.")
        traceback.print_exc()
    except PartialCredentialsError:
        print("Incomplete AWS credentials provided.")
        traceback.print_exc()
    except Exception as e:
        print("An unexpected error occurred:")
        traceback.print_exc()

# Example usage
if __name__ == "__main__":
    try:
        # Create a Boto3 client for Organizations
        client = boto3.client('organizations')
        
        # Define the output directory for CSV
        output_directory = './output'

        # Call the main function
        get_account_details(client, output_directory)
    
    except Exception as e:
        print("Failed to execute the script:")
        traceback.print_exc()
