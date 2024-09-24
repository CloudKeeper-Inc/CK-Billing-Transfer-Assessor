import os
import boto3
import csv
from datetime import datetime, timedelta

def get_all_accounts():
    """Retrieve all AWS accounts in the organization."""
    org_client = boto3.client('organizations')
    accounts = []

    paginator = org_client.get_paginator('list_accounts')
    for page in paginator.paginate():
        accounts.extend(page['Accounts'])

    return accounts

def get_cost_and_usage(start_date, end_date, account_id):
    """Retrieve cost and usage data for a specific account from AWS Cost Explorer."""
    cost_explorer_client = boto3.client('ce')

    response = cost_explorer_client.get_cost_and_usage(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Granularity='MONTHLY',
        Filter={
            'Dimensions': {
                'Key': 'LINKED_ACCOUNT',
                'Values': [account_id]
            }
        },
        Metrics=['UnblendedCost'],
        GroupBy=[
            {
                'Type': 'DIMENSION',
                'Key': 'SERVICE'
            }
        ]
    )

    return response

def parse_cost_data(response, account_id, account_name):
    """Parse the cost and usage data to get service-wise billing."""
    results = []
    for result in response['ResultsByTime']:
        time_period = result['TimePeriod']
        for group in result['Groups']:
            service = group['Keys'][0]
            amount = group['Metrics']['UnblendedCost']['Amount']
            results.append([account_id, account_name, time_period['Start'], time_period['End'], service, amount])
    return results

def export_to_csv(data, filename):
    """Export the billing data to a CSV file."""
    header = ['Account ID', 'Account Name', 'Start Date', 'End Date', 'Service', 'Cost']

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data)

    print(f"Data successfully exported to CSV.")

if __name__ == "__main__": 
    # Step 1: Get the current date and calculate the first and last day of the previous month
    today = datetime.today()
    first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_day_last_month = today.replace(day=1) - timedelta(days=1)

    start_date = first_day_last_month.strftime('%Y-%m-%d')
    end_date = last_day_last_month.strftime('%Y-%m-%d')
    print(start_date, end_date)
    start_date='2024-09-15'
    end_date='2024-09-20'

    # Step 2: Get all accounts in the organization
    accounts = get_all_accounts()

    # List to store the parsed cost data
    # all_billing_data = []

    # Step 3: Iterate over each account and get billing data
    for account in accounts:
        account_id = account['Id']
        account_name = account['Name']
        print(f"Fetching billing data for account: {account_name} ({account_id})")

        # Step 4: Get the cost and usage data for the account
        cost_data = get_cost_and_usage(start_date, end_date, account_id)

        # Step 5: Parse the data and add to the final result list
        account_billing_data = parse_cost_data(cost_data, account_id, account_name)
        # all_billing_data.extend(account_billing_data)
        export_to_csv(account_billing_data, filename=f'{account_id}_bill.csv')

def get_billing_info(output_directory):
    # Ensure the policy content directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Step 1: Get the current date and calculate the first and last day of the previous month
    today = datetime.today()
    first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_day_last_month = today.replace(day=1) - timedelta(days=1)

    start_date = first_day_last_month.strftime('%Y-%m-%d')
    end_date = last_day_last_month.strftime('%Y-%m-%d')
    # print(start_date, end_date)

    # Step 2: Get all accounts in the organization
    accounts = get_all_accounts()

    # List to store the parsed cost data
    # all_billing_data = []

    # Step 3: Iterate over each account and get billing data
    for account in accounts:
        account_id = account['Id']
        account_name = account['Name']
        print(f"Fetching billing data for account: {account_name} ({account_id})")

        # Step 4: Get the cost and usage data for the account
        cost_data = get_cost_and_usage(start_date, end_date, account_id)

        # Step 5: Parse the data and add to the final result list
        account_billing_data = parse_cost_data(cost_data, account_id, account_name)
        # all_billing_data.extend(account_billing_data)
        export_to_csv(account_billing_data, filename=f'{output_directory}/{account_id}_bill.csv')

