import boto3
import json
import datetime
import pandas as pd

ec2_client = boto3.client('ec2')
elb_client = boto3.client('elbv2')
rds_client = boto3.client('rds')
elasticache_client = boto3.client('elasticache')

instances = ec2_client.describe_instances()
balancers = elb_client.describe_load_balancers()
dbinstances = rds_client.describe_db_instances()




def get_all_rules(output = False):
    security_group_dict = ec2_client.describe_security_groups()
    security_group_rules = security_group_dict['SecurityGroups']
    security_rules = []
    for rules_dict in security_group_rules:
        security_rule = {}
        security_rule['GroupId'] = rules_dict['GroupId']
        security_rule['rules'] = []
        for rules in rules_dict['IpPermissions']:
            rule = {}
            if rules['IpProtocol'] == '-1':
                rule['IpProtocol'] = 'ALL'
                rule['port'] = '0-65535'
            else:
                rule['IpProtocol'] = rules['IpProtocol']
                rule['port'] = str(rules['FromPort']) if rules['FromPort'] == rules['ToPort'] else str(rules['FromPort']) +'-'+ str(rules['ToPort'])
            rule['IpRanges'] = rules['IpRanges']
            security_rule['rules'].append(rule)
        security_rules.append(security_rule)
    if output is True:
        with open("all_rules.json","w") as t:
            t.write(json.dumps(security_rules))
    return security_rules

def get_all_balancers(output = False,readonline = False):
    if readonline is False:
        security_group_rules = get_all_rules()
    else:
        with open("./data/all_rules.json","r") as t:
            security_group_rules = json.load(t)
    balancers_list = []
    for elb in balancers['LoadBalancers']:
        if elb['Type'] == 'application':
            balancers_dict = {}
            balancers_dict['Name'] = elb['DNSName']
            balancers_dict['VpcId'] = elb['VpcId']
            SecurityGroups_ids = []
            rules_list = []
            for security_ids in elb['SecurityGroups']:
                SecurityGroups_ids.append(security_ids)
                for a in range(len(security_group_rules)):
                        if security_ids == security_group_rules[a]['GroupId']:
                            rules_list.append(security_group_rules[a]['rules'])
            balancers_dict['SecurityGroups'] = SecurityGroups_ids
            balancers_dict['Security_rules'] = rules_list
            balancers_list.append(balancers_dict)
    if output is True:
        with open("./data/all_balancers.json","w") as t:
            t.write(json.dumps(balancers_list))
    return balancers_list

def get_all_instances(output = False,readonline = False):
    if readonline is False:
        security_group_rules = get_all_rules()
    else:
        with open("./data/all_rules.json","r") as t:
            security_group_rules = json.load(t)
    instance_list = []
    for i in instances['Reservations']:
        instance_dict = {}
        for ec2 in i['Instances']:
            if ec2['State']['Name'] == 'running':
                print(ec2)
                instance_dict['InstanceId'] = ec2['InstanceId']
                instance_dict['InstanceType'] = ec2['InstanceType']
                instance_dict['PrivateIpAddress'] = ec2['PrivateIpAddress']
                instance_dict['PublicIpAddress'] = ec2['PublicIpAddress']
                instance_dict['VpcId'] = ec2['VpcId']
                for n in ec2['Tags']:
                    instance_dict[n['Key']] = n['Value']
                    if n.get('name'):
                        instance_dict['name'] = n['Value']
                SecurityGroups_ids = []
                rules_list = []
                for m in ec2['SecurityGroups']:
                    SecurityGroups_ids.append(m['GroupId'])
                    for a in range(len(security_group_rules)):
                        if m['GroupId'] == security_group_rules[a]['GroupId']:
                            rules_list.append(security_group_rules[a]['rules'])
                instance_dict['SecurityGroups'] = SecurityGroups_ids    
                instance_dict['Security_rules'] = rules_list
                instance_list.append(instance_dict)
    if output is True:
        with open("./data/all_instances.json","w") as t:
            t.write(json.dumps(instance_list))
    return instance_list





# balancers_list = get_all_balancers(output = True,readonline = False)
# with open("./data/elb.json","w") as a:
#     pd.DataFrame(balancers_list).to_csv('./data/elb.csv')


instances_list = get_all_instances(output = True,readonline = False)
with open("./data/ec2.json","w") as a:
    pd.DataFrame(instances_list).to_csv('./data/ec2.csv')
