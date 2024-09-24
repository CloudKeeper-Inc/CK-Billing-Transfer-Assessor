import csv

def get_org_enabled_services(client):
    # Get the list of AWS services enabled for the organization
    services = []
    paginator = client.get_paginator('list_aws_service_access_for_organization')
    for page in paginator.paginate():
        services.extend(page['EnabledServicePrincipals'])
    return services

def write_services_to_csv(services, file_name):
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

def get_org_services(client, outputDirectory):
    # Step 1: Get organization-enabled services
    print("Fetching organization-enabled services...")
    services = get_org_enabled_services(client)
    # print(services)
    
    # Step 2: Write organization-enabled services to CSV
    print("Writing organization-enabled services to CSV...")
    write_services_to_csv(services, f'{outputDirectory}/org_services.csv')
    # print(ssoEnabled)
