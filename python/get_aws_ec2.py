# coding: utf-8
import boto3
import json
import pandas as pd

ec2_client = boto3.client('ec2')
instances = ec2_client.describe_instances()

def getINstance(output = False,readonline = False):
    instance_list = []
    for i in instances['Reservations']:
        instance_dict = {}
        for ec2 in i['Instances']:
            if ec2['State']['Name'] == 'running':
                print(ec2)
                instance_dict['InstanceId'] = ec2['InstanceId']
                instance_dict['InstanceType'] = ec2['InstanceType']
                instance_dict['PrivateIpAddress'] = ec2['PrivateIpAddress']
                instance_dict['VpcId'] = ec2['VpcId']
                instance_dict['InstanceType'] = ec2['InstanceType']
                for n in ec2['Tags']:
                    instance_dict[n['Key']] = n['Value']
                    if n.get('name'):
                        instance_dict['name'] = n['Value']
                instance_list.append(instance_dict)
    if output is True:
        with open("./instances.json","w") as t:
            t.write(json.dumps(instance_list))
    return instance_list
if __name__ == '__main__':
    instances_list = getINstance(output = True,readonline = False)
    with open("./ec2.json","w",) as a:
        pd.DataFrame(instances_list).to_csv('./ec2.csv')