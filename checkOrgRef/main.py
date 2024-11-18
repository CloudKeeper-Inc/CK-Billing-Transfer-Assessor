import boto3
import sys,os,datetime,re
from utility import get_regions
from sns import check_organization_references_in_sns_policy
from sqs import check_organization_references_in_sqs_policy
from s3 import checks3
from iam_policies import check_iam_policies
from iam_roles_trust_policy import check_iam_roles_trust_policy
from ecr import check_organization_references_in_policy

regionList = get_regions()
for region in regionList:
    org_id_pattern = re.compile(r'\bo-[a-zA-Z0-9]{4,32}\b')

    check_organization_references_in_sns_policy(region,org_id_pattern)
    check_organization_references_in_sqs_policy(region,org_id_pattern)
    checks3(org_id_pattern)
    check_iam_roles_trust_policy(org_id_pattern)
    check_iam_policies(org_id_pattern)
    check_organization_references_in_policy(org_id_pattern)


        

