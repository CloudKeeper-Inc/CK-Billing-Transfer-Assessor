README.md
This repository has the code for the onboarding automation scripts. The checkOrgRef directory contains scripts to check for organisation ids present in multiple IAM policies.

Usage:
make sure to have boto3 installed and the correct aws credentials configured

To check for organisation dependencies:
python3 main.py

To check for organisation id references in policies :
cd checkOrgRef
python3 main.py

!! To check for individual services you can run individual scripts as well