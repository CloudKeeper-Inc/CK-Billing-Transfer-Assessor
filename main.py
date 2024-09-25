import os
import boto3
import boto3.session
import traceback
from aws_accounts import get_account_details
from org_services import get_org_services
from policies import get_policies
from sso import get_sso_info
from billing import get_billing_info
import zipfile
import shutil
from ram import check_for_non_shareable_resources

output_directory = ''

def zip_folder(folder_path, zip_file_path):
    """Zips the contents of an entire folder."""
    try:
        with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Walk the directory tree
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Write the file to the zip file, but omit the folder structure in the zip
                    zipf.write(file_path, os.path.relpath(file_path, folder_path))

        print(f"Folder '{folder_path}' zipped successfully as '{zip_file_path}'")

        # Remove the folder as the zip remains
        shutil.rmtree(folder_path)
    except Exception as e:
        print(f"Error in zip_folder for {folder_path}:")
        print(traceback.format_exc())
        raise

def main():
    try:
        # Initialize a single boto3 client for AWS Organizations
        orgClient = boto3.client('organizations', region_name=boto3.Session().region_name)  # Using the current region

        # Ensure the output directory exists
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        # Getting account details
        print("\n--- Getting Accounts related info ---\n")
        get_account_details(orgClient, output_directory)

        # Getting all the org services that are currently enabled
        print("\n--- Checking if Org Based services are in use ---\n")
        get_org_services(orgClient, output_directory)

        # Getting the different policies that are enabled at the org level
        print("\n--- Checking if any Policies are in use ---\n")
        policyContentDir = f"{output_directory}/policy_content"
        get_policies(orgClient, output_directory, policyContentDir)

        # Getting SSO-related info into a separate directory
        print("\n--- Checking if SSO is enabled ---\n")
        get_sso_info(f'{output_directory}/IdentityCenter')

        # Getting billing-related info into a separate directory
        print("\n--- Checking Billing data if Org services are enabled ---\n")
        get_billing_info(f'{output_directory}/Billing')

        # Getting RAM-related info
        print("\n--- Checking RAM if any org dependent resources are shared ---\n")
        check_for_non_shareable_resources(output_directory)

        # Zip all contents and remove folder
        print("\n--- Creating downloadable zip ---\n")
        zip_folder(folder_path=output_directory, zip_file_path=f'{output_directory}.zip')

    except Exception as e:
        print("Error in main execution:")
        print(traceback.format_exc())
        raise

if __name__ == "__main__":
    try:
        outputDirInput = input("\n Please enter your organisation's name: ")
        # Output directory, replace spaces with underscores
        output_directory = outputDirInput.replace(' ', '_')
        main()

        current_directory = os.getcwd()
        print(f"\nPlease download the zip from path : {current_directory}/{output_directory}.zip\n")
    except Exception as e:
        print("An error occurred in the main program:")
        print(traceback.format_exc())
