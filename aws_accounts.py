import csv

rootAccountId=''

def get_aws_accounts(client):
    # List all the accounts in the organization
    accounts = []
    paginator = client.get_paginator('list_accounts')
    for page in paginator.paginate():
        accounts.extend(page['Accounts'])
    return accounts

def identify_root_account(client):
    # The root (management) account is the one with "INVITED" as its 'JoinedMethod'.
    root_account = None
    response=client.describe_organization()
    organization = response['Organization']
    root_account_id = organization['MasterAccountId']
    global rootAccountId
    rootAccountId=root_account_id
    return root_account_id
    

def write_accounts_to_csv(accounts, root_account_id, file_name):
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

def get_account_details(client,outputDirectory):
    # Step 1: Get AWS accounts and root account
    print("Fetching AWS accounts...")
    accounts = get_aws_accounts(client)
    root_account_id = identify_root_account(client)
    
    # Step 2: Write AWS accounts to CSV
    print("Writing AWS accounts to CSV...")
    write_accounts_to_csv(accounts, root_account_id, f'{outputDirectory}/aws_accounts.csv')
    
