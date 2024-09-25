import csv
import traceback

def get_org_enabled_services(client):
    """Get the list of AWS services enabled for the organization."""
    try:
        services = []
        paginator = client.get_paginator('list_aws_service_access_for_organization')
        for page in paginator.paginate():
            services.extend(page['EnabledServicePrincipals'])
        return services
    except Exception as e:
        print("Error in get_org_enabled_services:")
        print(traceback.format_exc())
        raise  # Re-raise the exception after logging it

def write_services_to_csv(services, file_name):
    """Write the organization-enabled services to a CSV file."""
    try:
        # Define the header for the CSV file
        header = ['Service Principal', 'Date Enabled']

        # Open the CSV file for writing
        with open(file_name, mode='w', newline='') as file:
            writer = csv.writer(file)

            # Write the header
            writer.writerow(header)

            # Write the service data
            for service in services:
                writer.writerow([service['ServicePrincipal'], service['DateEnabled']])
    except Exception as e:
        print(f"Error in write_services_to_csv when writing to {file_name}:")
        print(traceback.format_exc())
        raise

def get_org_services(client, outputDirectory):
    """Main function to get organization-enabled services and write them to a CSV file."""
    try:
        # Step 1: Get organization-enabled services
        print("Fetching organization-enabled services...")
        services = get_org_enabled_services(client)

        # Step 2: Write organization-enabled services to CSV
        print("Writing organization-enabled services to CSV...")
        write_services_to_csv(services, f'{outputDirectory}/org_services.csv')

    except Exception as e:
        print("Error in get_org_services:")
        print(traceback.format_exc())
        raise

if __name__ == "__main__":
    try:
        # Assume 'client' and 'outputDirectory' are set elsewhere in the actual implementation
        client = None  # Replace this with actual boto3 client initialization
        outputDirectory = 'output'  # Replace with the actual output directory
        get_org_services(client, outputDirectory)
    except Exception as e:
        print("An error occurred in the main program:")
        print(traceback.format_exc())
