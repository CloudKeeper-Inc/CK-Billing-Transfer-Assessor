import boto3
import datetime

all_regions = ['af-south-1','ap-northeast-1','ap-northeast-2','ap-northeast-3','ap-southeast-1',
               'ap-southeast-2','ap-southeast-3','ap-south-1','ca-central-1','eu-central-1',
               'eu-north-1','eu-west-1','eu-west-2','eu-west-3','eu-south-1','us-west-1','us-west-2',
               'us-east-1','us-east-2','sa-east-1','ap-east-1','me-south-1']

def get_regions():
    final_regions = ''
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=15)
    client = boto3.client('ce',region_name = 'us-east-1')
    response = client.get_cost_and_usage(
        TimePeriod={
        'Start': str(start_date),
        'End': str(end_date)
        },
        Metrics=['UnblendedCost'],
        Granularity='MONTHLY',
        GroupBy = [
            {
            'Type': 'DIMENSION',
            'Key': 'REGION'
            },]
    )
    result = response['ResultsByTime'][0]['Groups']
    regions = []
    regionList = []
    for i in range(len(result)):
        cost = float(result[i]['Metrics']['UnblendedCost']['Amount'])
        region_code = result[i]['Keys']
        if cost > 1:
            regions.append(region_code)
            res = [''.join(ele) for ele in regions]
            final_regions = [ region for region in res if region in all_regions ]

    regions_list= ",".join(final_regions)
    regionList.extend(final_regions)
    print(f'Optimal regions: {final_regions}')
    print(type(final_regions))

    enabled_regions = []
    region_list_final = []
    ec2 = boto3.client('ec2',region_name='us-east-1')
    data = ec2.describe_regions()
    for region in data['Regions']:
        enabled_regions.append(region['RegionName'])
    for optimal in regionList:
        for enabled in enabled_regions:
            if optimal == enabled:
                region_list_final.append(optimal)
    return region_list_final
