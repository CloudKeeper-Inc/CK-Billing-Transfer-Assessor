import os
import boto3
import csv
from botocore.exceptions import NoCredentialsError, ClientError
from find_sso_region import find_region_with_sso
from aws_accounts import get_aws_accounts
import traceback

def get_user_details_and_export_to_csv(identity_store_client, csv_file, identity_store_id):
    """
    Fetches user details from AWS Identity Center (SSO) and exports them to a CSV file.
    
    :param csv_file: The path of the CSV file to write the user info.
    """
    try:
        users_response = identity_store_client.list_users(
            IdentityStoreId=identity_store_id
        )

        users = users_response.get('Users', [])
        if not users:
            print("No users found in the Identity Center.")
            return

        # Prepare the CSV file for writing
        with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Write the header row
            writer.writerow(['UserName', 'DisplayName', 'Email', 'UserId'])

            # Write user details to the CSV file
            for user in users:
                user_id = user.get('UserId', 'N/A')
                user_name = user.get('UserName', 'N/A')
                display_name = user.get('DisplayName', 'N/A')
                email = user.get('Emails', [{'Value': 'N/A'}])[0]['Value']

                # Write the user row
                writer.writerow([user_name, display_name, email, user_id])

        print(f"User info exported successfully to CSV.")

    except NoCredentialsError:
        print("AWS credentials not found. Please configure your AWS CLI.")
    except ClientError as e:
        print(f"An error occurred while fetching user details: {e}")
        print(traceback.format_exc())
    except Exception as e:
        print(f"Unexpected error in get_user_details_and_export_to_csv: {e}")
        print(traceback.format_exc())

def get_groups_and_export_to_csv(identity_store_client, csv_file, identity_store_id):
    """
    Fetches group details from AWS Identity Center (SSO) and exports them to a CSV file.
    
    :param csv_file: The path of the CSV file to write the group info.
    :param identity_store_id: The Identity Store ID.
    """
    try:
        groups_response = identity_store_client.list_groups(
            IdentityStoreId=identity_store_id
        )

        groups = groups_response.get('Groups', [])
        if not groups:
            print("No groups found in the Identity Center.")
            return

        # Prepare the CSV file for writing
        with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Write the header row
            writer.writerow(['GroupName', 'GroupId'])

            # Write group details to the CSV file
            for group in groups:
                group_name = group.get('DisplayName', 'N/A')
                group_id = group.get('GroupId', 'N/A')

                # Write the group row
                writer.writerow([group_name, group_id])

        print(f"Group info exported successfully to CSV.")

    except NoCredentialsError:
        print("AWS credentials not found. Please configure your AWS CLI.")
    except ClientError as e:
        print(f"An error occurred while fetching group details: {e}")
        print(traceback.format_exc())
    except Exception as e:
        print(f"Unexpected error in get_groups_and_export_to_csv: {e}")
        print(traceback.format_exc())

def get_permission_sets_and_export_to_csv(sso_client, csv_file, instance_arn):
    """
    Fetches permission set details from AWS Identity Center (SSO) and exports them to a CSV file.
    
    :param csv_file: The path of the CSV file to write the permission set info.
    :param instance_arn: The Identity Center Instance ARN.
    """
    try:
        permission_sets_response = sso_client.list_permission_sets(
            InstanceArn=instance_arn
        )

        permission_sets = permission_sets_response.get('PermissionSets', [])
        if not permission_sets:
            print("No permission sets found in the Identity Center.")
            return

        # Prepare the CSV file for writing
        with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Write the header row
            writer.writerow(['PermissionSetArn'])

            # Write permission set details to the CSV file
            for permission_set in permission_sets:
                writer.writerow([permission_set])

        print(f"Permission sets info exported successfully to CSV.")

    except NoCredentialsError:
        print("AWS credentials not found. Please configure your AWS CLI.")
    except ClientError as e:
        print(f"An error occurred while fetching permission sets: {e}")
        print(traceback.format_exc())
    except Exception as e:
        print(f"Unexpected error in get_permission_sets_and_export_to_csv: {e}")
        print(traceback.format_exc())

def get_sso_applications_and_export_to_csv(sso_client, csv_file, instance_arn):
    """
    Fetches SSO applications from AWS Identity Center (SSO) and exports them to a CSV file.
    
    :param csv_file: The path of the CSV file to write the application info.
    :param instance_arn: The Identity Center Instance ARN.
    """
    try:
        applications_response = sso_client.list_applications(
            InstanceArn=instance_arn
        )

        applications = applications_response.get('Applications', [])
        if not applications:
            print("No SSO applications found in the Identity Center.")
            return

        # Prepare the CSV file for writing
        with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Write the header row
            writer.writerow(['ApplicationArn', 'DisplayName', 'Status'])

            # Write application details to the CSV file
            for app in applications:
                app_id = app.get('ApplicationArn', 'N/A')
                display_name = app.get('Name', 'N/A')
                app_type = app.get('Status', 'N/A')

                # Write the application row
                writer.writerow([app_id, display_name, app_type])

        print(f"SSO application info exported successfully to CSV.")

    except NoCredentialsError:
        print("AWS credentials not found. Please configure your AWS CLI.")
    except ClientError as e:
        print(f"An error occurred while fetching SSO applications: {e}")
        print(traceback.format_exc())
    except Exception as e:
        print(f"Unexpected error in get_sso_applications_and_export_to_csv: {e}")
        print(traceback.format_exc())

def get_account_permission_sets_and_export_to_csv(sso_client, csv_file, instance_arn):
    """
    Fetches permission sets attached to AWS accounts and exports them to a CSV file.
    
    :param csv_file: The path of the CSV file to write the permission set info.
    :param instance_arn: The Identity Center Instance ARN.
    """
    try:
        # Getting all aws accounts
        accounts = get_aws_accounts(boto3.client('organizations'))

        # Initialize number of applications required post transition to 0
        number_of_applications_required = 0 

        # Prepare the CSV file for writing
        with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Write the header row
            writer.writerow(['AccountId', 'PermissionSetCount'])

            for account in accounts:
                acc_id = account['Id']
                permission_set_response = sso_client.list_permission_sets_provisioned_to_account(
                    AccountId=acc_id,
                    InstanceArn=instance_arn    
                )
                permission_set_count = len(permission_set_response['PermissionSets'])
                
                # Incrementing number of applications required as per the found permission sets
                number_of_applications_required += permission_set_count

                writer.writerow([acc_id, permission_set_count])
            
            # Appending final number of applications required
            writer.writerow(['Total applications required', number_of_applications_required])
            
            print(f"Permission set attachment info exported successfully to CSV.")

    except NoCredentialsError:
        print("AWS credentials not found. Please configure your AWS CLI.")
    except ClientError as e:
        print(f"An error occurred while fetching account permission sets: {e}")
        print(traceback.format_exc())
    except Exception as e:
        print(f"Unexpected error in get_account_permission_sets_and_export_to_csv: {e}")
        print(traceback.format_exc())

if __name__ == '__main__': 
    try:
        # Initialize the boto3 client for AWS Identity Center
        sso_client = boto3.client('sso-admin')
        response = sso_client.list_instances()
        if response['Instances']:
            print('SSO enabled in current region, skipping region checks!')
            sso_region = boto3.Session().region_name
        else:
            # Checking other regions 
            sso_region = find_region_with_sso()
        
        print(sso_region)

        if sso_region:
            # Create required clients
            sso_client = boto3.client('sso-admin', region_name=sso_region)
            identity_store_client = boto3.client('identitystore', sso_region)
            
            # Fetch Identity Center Instance and Identity Store ID
            instances_response = sso_client.list_instances()
            identity_center_instance_id = instances_response['Instances'][0]['InstanceArn']
            identity_store_id = instances_response['Instances'][0]['IdentityStoreId']
            
            # Specify the paths to your CSV files
            # user_csv_file = 'identity_center_users.csv'
            # group_csv_file = 'identity_center_groups.csv'
            # permission_set_csv_file = 'identity_center_permission_sets.csv'
            # sso_applications_csv_file = 'identity_center_sso_applications.csv'
            # account_permission_set_count_csv_file = 'identity_center_permission_sets_attached_to_account.csv'
            # get_account_permission_sets_and_export_to_csv(account_permission_set_count_csv_file, identity_center_instance_id)
            # # Export users
            # get_user_details_and_export_to_csv(identity_store_client, user_csv_file, identity_store_id)

            # # Export groups
            # get_groups_and_export_to_csv(identity_store_client, group_csv_file, identity_store_id)

            # # Export permission sets
            # get_permission_sets_and_export_to_csv(sso_client, permission_set_csv_file, identity_center_instance_id)

            # # Export SSO applications
            # get_sso_applications_and_export_to_csv(sso_client, sso_applications_csv_file, identity_center_instance_id)
        else:
            print("SSO not enabled")
    
    except Exception as e:
        print(f"Unexpected error in main: {e}")
        print(traceback.format_exc())

def get_sso_info(outputDirectory):
    """
    Retrieves SSO information and exports it to CSV files in the specified directory.
    
    :param outputDirectory: The directory where the CSV files will be saved.
    """
    try:
        # Creating directories if they don't exist
        if not os.path.exists(outputDirectory):
            os.makedirs(outputDirectory)

        # Checking if sso is enabled in current region
        sso_client = boto3.client('sso-admin')
        response = sso_client.list_instances()
        if response['Instances']:
            sso_region = boto3.Session().region_name
            print(f'SSO enabled in current region: {sso_region}, skipping region checks!')
        else:
            # Checking other regions 
            sso_region = find_region_with_sso()
            print(f'SSO enabled in region: {sso_region}')

        if sso_region:
            try:
                # Create required clients
                sso_client = boto3.client('sso-admin', region_name=sso_region)
                identity_store_client = boto3.client('identitystore', sso_region)
                
                # Fetch Identity Center Instance and Identity Store ID
                instances_response = sso_client.list_instances()
                identity_center_instance_arn = instances_response['Instances'][0]['InstanceArn']
                identity_store_id = instances_response['Instances'][0]['IdentityStoreId']
                
                # Specify the paths to your CSV files
                user_csv_file = f'{outputDirectory}/identity_center_users.csv'
                group_csv_file = f'{outputDirectory}/identity_center_groups.csv'
                permission_set_csv_file = f'{outputDirectory}/identity_center_permission_sets.csv'
                sso_applications_csv_file = f'{outputDirectory}/identity_center_sso_applications.csv'
                account_permission_set_count_csv_file = f'{outputDirectory}/identity_center_permission_sets_attached_to_account.csv'
                
                # Export users
                get_user_details_and_export_to_csv(identity_store_client, user_csv_file, identity_store_id)

                # Export groups
                get_groups_and_export_to_csv(identity_store_client, group_csv_file, identity_store_id)

                # Export permission sets
                get_permission_sets_and_export_to_csv(sso_client, permission_set_csv_file, identity_center_instance_arn)

                # Export SSO applications
                get_sso_applications_and_export_to_csv(sso_client, sso_applications_csv_file, identity_center_instance_arn)

                # Export permission sets attached to accounts
                get_account_permission_sets_and_export_to_csv(sso_client, account_permission_set_count_csv_file, identity_center_instance_arn)

            except Exception as e:
                print(f"Failed to retrieve Identity Center instances: {e}")
                print(traceback.format_exc())
        else:
            print("SSO not enabled")
    except Exception as e:
        print(f"Unexpected error in get_sso_info: {e}")
        print(traceback.format_exc())
