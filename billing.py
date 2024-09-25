import os
import boto3
import csv
from datetime import datetime, timedelta
import traceback

def get_all_accounts():
    """Retrieve all AWS accounts in the organization."""
    try:
        org_client = boto3.client('organizations')
        accounts = []

        paginator = org_client.get_paginator('list_accounts')
        for page in paginator.paginate():
            accounts.extend(page['Accounts'])

        return accounts
    except Exception as e:
        print(f"Error in get_all_accounts: {e}")
        print(traceback.format_exc())

def get_cost_and_usage(start_date, end_date, account_id):
    """Retrieve cost and usage data for a specific account from AWS Cost Explorer."""
    try:
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
    except Exception as e:
        print(f"Error in get_cost_and_usage for account {account_id}: {e}")
        print(traceback.format_exc())

def parse_cost_data(response, account_id, account_name):
    """Parse the cost and usage data to get service-wise billing."""
    try:
        results = []
        for result in response['ResultsByTime']:
            time_period = result['TimePeriod']
            for group in result['Groups']:
                service = group['Keys'][0]
                amount = group['Metrics']['UnblendedCost']['Amount']
                results.append([account_id, account_name, time_period['Start'], time_period['End'], service, amount])
        return results
    except KeyError as e:
        print(f"KeyError in parse_cost_data for account {account_id}: {e}")
        print(traceback.format_exc())
    except Exception as e:
        print(f"Unexpected error in parse_cost_data for account {account_id}: {e}")
        print(traceback.format_exc())

def export_to_csv(data, filename):
    """Export the billing data to a CSV file."""
    try:
        header = ['Account ID', 'Account Name', 'Start Date', 'End Date', 'Service', 'Cost']

        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(data)

        print(f"Info successfully exported to CSV.")
    except Exception as e:
        print(f"Error exporting to CSV {filename}: {e}")
        print(traceback.format_exc())

if __name__ == "__main__": 
    try:
        # Step 1: Get the current date and calculate the first and last day of the previous month
        today = datetime.today()
        first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        last_day_last_month = today.replace(day=1) - timedelta(days=1)

        start_date = first_day_last_month.strftime('%Y-%m-%d')
        end_date = last_day_last_month.strftime('%Y-%m-%d')
        print(start_date, end_date)

        # Step 2: Get all accounts in the organization
        accounts = get_all_accounts()

        # Step 3: Iterate over each account and get billing data
        for account in accounts:
            account_id = account['Id']
            account_name = account['Name']
            print(f"Fetching billing info for account: {account_name} ({account_id})")

            # Step 4: Get the cost and usage data for the account
            cost_data = get_cost_and_usage(start_date, end_date, account_id)
            if cost_data is None:
                continue  # Skip to next account if cost data retrieval failed

            # Step 5: Parse the data and add to the final result list
            account_billing_data = parse_cost_data(cost_data, account_id, account_name)
            if account_billing_data is not None:
                export_to_csv(account_billing_data, filename=f'{account_id}_bill.csv')

    except Exception as e:
        print(f"Unexpected error in main: {e}")
        print(traceback.format_exc())

def get_billing_info(output_directory):
    try:
        # Ensure the policy content directory exists
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        # Step 1: Get the current date and calculate the first and last day of the previous month
        today = datetime.today()
        first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        last_day_last_month = today.replace(day=1) - timedelta(days=1)

        start_date = first_day_last_month.strftime('%Y-%m-%d')
        end_date = last_day_last_month.strftime('%Y-%m-%d')

        # Step 2: Get all accounts in the organization
        accounts = get_all_accounts()

        # Step 3: Iterate over each account and get billing data
        for account in accounts:
            account_id = account['Id']
            account_name = account['Name']
            print(f"Fetching billing data for account: {account_name} ({account_id})")

            # Step 4: Get the cost and usage data for the account
            cost_data = get_cost_and_usage(start_date, end_date, account_id)
            if cost_data is None:
                continue  # Skip to next account if cost data retrieval failed

            # Step 5: Parse the data and add to the final result list
            account_billing_data = parse_cost_data(cost_data, account_id, account_name)
            if account_billing_data is not None:
                export_to_csv(account_billing_data, filename=f'{output_directory}/{account_id}_bill.csv')

    except Exception as e:
        print(f"Unexpected error in get_billing_info: {e}")
        print(traceback.format_exc())
