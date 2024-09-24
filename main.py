import os
import boto3
import boto3.session
from aws_accounts import get_account_details
from org_services import get_org_services
from policies import get_policies
from sso import get_sso_info
from billing import get_billing_info
import zipfile,shutil
from ram import check_for_non_shareable_resources

output_directory=''

def zip_folder(folder_path, zip_file_path):
    """Zips the contents of an entire folder."""
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Walk the directory tree
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                # Write the file to the zip file, but omit the folder structure in the zip
                zipf.write(file_path, os.path.relpath(file_path, folder_path))

    print(f"Folder '{folder_path}' zipped successfully as '{zip_file_path}'")

    shutil.rmtree(folder_path) # remove the folder as zip remains


def main():
    # Initialize a single boto3 client for AWS Organizations
    orgClient = boto3.client('organizations', region_name=boto3.Session().region_name) # using the current region

    # Ensure the output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    #Getting account details
    get_account_details(orgClient,output_directory)
    
    #Getting all the org services that are currently enabled
    get_org_services(orgClient, output_directory)
    
    #Getting the different policies that are enabled at org level
    policyContentDir=f"{output_directory}/policy_content"
    get_policies(orgClient, output_directory, policyContentDir)

    #Getting SSO related info into a separate directory
    get_sso_info(f'{output_directory}/IdentityCenter')

    #Getting billing related info into a separate directory
    get_billing_info(f'{output_directory}/Billing')

    #Getting RAM related info
    check_for_non_shareable_resources(output_directory)

    #zip all contents and remove folder
    zip_folder(folder_path=output_directory, zip_file_path=f'{output_directory}.zip')


if __name__ == "__main__":
    outputDirInput=input("Please enter your organisation's name : ")
    # outputDirectory='testorg'
    output_directory=outputDirInput.replace(' ', '_')  # Replace spaces with underscores
    main()

