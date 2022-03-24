#!/usr/bin/env python3
# import netmiko, time
import telnetlib, time
import os
import sys
import requests
from urllib.parse import urljoin
import json
import logging
import re
import boto3
from botocore.exceptions import ClientError, ConnectionError, ConnectTimeoutError







logging.basicConfig(filename='update.log', level=logging.INFO,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d')

device = {
    'ip':'10.0.200.1',
    'username':'wlk',
    'password':'gBuPTJ0DlWwY9cb2',
}
security_group_id = {
    "prod":"sg-06f8e6eccd6ea942c",
    "demo":"sg-0153fb7a823ee012a"
}
def getWanIPs():
    result = []
    partern = r'\d+\.\d+\.\d+\.\d+'

    try:
        tn = telnetlib.Telnet(device['ip'])
        # DEBUG LEVEL SETTINGS
        # tn.set_debuglevel(5)
        tn.read_until('login: '.encode(), timeout=2)
        tn.write(device['username'].encode() + b'\n')
        tn.read_until('Password: '.encode(), timeout=2)
        tn.write(device['password'].encode() + b'\n')
        tn.write(b'\n')
        time.sleep(2)
        tn.write('display interface brief'.encode() + b'\n')
        res = tn.read_until('---- More ----'.encode(), 2)
        # print(res.decode(encoding='utf8'))
        for line in res.decode(encoding='utf8').split('\r\r\n'):
            if 'Dia' in str(line):
                ip = line.strip().split(' ')[-1]
                if re.match(pattern=partern, string=ip):
                    result.append(ip)
                    # print('[ {ip} ] is valid'.format(ip=ip))

                else:
                    print('[ {ip} ] is not a valid ip address'.format(ip=ip))
                    logging.warning('[ {ip} ] is not a valid ip address'.format(ip=ip))
        # print('Success!')
        # print('WAN IP LIST {}'.format(result))
        return result

    except Exception as e:
        print(e)
    finally:
        tn.close()



class CloudFlare:
    def __init__(self, apiKey, email):

        self.apiKey = apiKey
        self.email = email

    @property
    def baseURL(self):
        return "https://api.cloudflare.com/client/v4/"
    @property
    def headers(self):
        return {
            "Content-Type":"application/json",
            "X-Auth-Key":self.apiKey,
            "X-Auth-Email":self.email
        }


# print(getWanIPs())

    def listZones(self):
        # headers = {
        #     "Content-Type":"application/json",
        #     "X-Auth-Key":"195fe85f74228c6650c99dbb1357ad3b75499",
        #     "X-Auth-Email":"weidezhu@oneroot.io"
        #
        # }
        # print(parse(baseURL, 'zone'))
        res = requests.get(urljoin(self.baseURL, 'zones'), headers=self.headers)
        return json.loads(res.content.decode())
    def getZone(self, name):
        __zone = None
        if self.listZones()['success']:

            for zone in self.listZones()['result']:
                if zone['name'] == name:
                    __zone = zone
        else:
            print('Failed to fetch zones : ')
            print(self.listZones())

        return __zone

    def getZoneIdByName(self, name):
        return self.getZone(name)['id']


    def getWAFPackages(self,zone):
        try:
            url = urljoin(self.baseURL, 'zones/{}/firewall/waf/packages'.format(self.getZoneIdByName(name=zone)))
            print(url)
            res = requests.get(url, headers=self.headers)
            return json.loads(res.content.decode())
        except Exception as e:
            print(e)

    def getPackageIdbyName(self, zone, packageName):
        for package in self.getWAFPackages(zone)['result']:
            # print(package)
            if package['name'] == packageName:
                return package['id']
    def listFirewallRules(self, zone):
        try:
            url = urljoin(self.baseURL, 'zones/{}/firewall/rules'.format(self.getZoneIdByName(zone)))
            res = requests.get(url, headers=self.headers)
            return json.loads(res.content.decode())
        except Exception as e:
            print(e)
    def getFirewallRuleIdByDescription(self, zone, description):
        for rule in self.listFirewallRules(zone)['result']:
            if rule['description'] == description:
                return rule['id']
    def listFirewallFilters(self,zone):
        try:
            url = urljoin(self.baseURL, 'zones/{}/filters'.format(self.getZoneIdByName(zone)))
            res = requests.get(url, headers = self.headers)
            return json.loads(res.content.decode())
        except Exception as e:
            print(e)

    def getFirewallFilterIdByName(self, zone, filter_name):
        for _filter in self.listFirewallFilters(zone)['result']:
            if _filter['description'] == filter_name:
                return _filter['id']
    def updateFirewallFilter(self, zone, description_name, filter_content):
        try:
            print('Updating {} in zone {}'.format(description_name, zone))
            print('Update data : ')
            print(filter_content)
            url = urljoin(self.baseURL, 'zones/{}/filters/{}'.format(self.getZoneIdByName(zone), self.getFirewallFilterIdByName(zone, description_name)))
            if isinstance(filter_content, dict):
                res = requests.put(url, headers=self.headers, data=json.dumps(filter_content))
                print(res.text)
                return json.loads(res.content.decode())
            else:
                print('filter_content is not a valid dict')
        except Exception as e:
            print(e)

    def createFirewallRule(self):
        pass


def generate_expression():
    ip_list = getWanIPs()
    default_string = ''
    if len(ip_list) < 1:
        raise ValueError('No valid ip address found from firewall')
    else:
        for i in range(len(ip_list)):
            if i < len(ip_list) - 1:
                default_string += '(ip.src eq {})'.format(ip_list[i]) + ' or '
            else:
                default_string += '(ip.src eq {})'.format(ip_list[i])
        return default_string
def usage():
    print('=' * 100 + '\n')
    print('    Python3 interpreter is REQUIRED to run\n')
    print('    This script is used for fetching apbc WAN ip addresses\n')
    print('    argument updateCloudFlare will update the apbc wan ip of allow_office rule on cloudflare\n')
    print('    python3 {} [ get-ip | updateCloudFlare | list-aws-sg | update-aws | help ]\n'.format(sys.argv[0]))

class AWSSecurityGroup:
    def __init__(self, region_name, aws_access_key_id, aws_secret_access_key):
        self.region_name = region_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        try:
            self.client = boto3.client('ec2',
                                       region_name=self.region_name,
                                       aws_access_key_id=self.aws_access_key_id,
                                       aws_secret_access_key=self.aws_secret_access_key)
        except ClientError as clientErr:
            logging.ERROR(clientErr)
        except ConnectTimeoutError as connectionErr:
            logging.ERROR(connectionErr)
        except ConnectTimeoutError as timeoutErr:
            logging.ERROR(timeoutErr)
        except Exception as err:
            logging.ERROR(err)

    def getSecurityGroupDescription(self,GroupIds):
        groups = self.client.describe_security_groups(
            GroupIds=GroupIds
        )
        return groups
    def addSecurityGroupIngress(self,**kwargs):
        try:
            data = self.client.authorize_security_group_ingress(**kwargs)
            return data
        except ClientError:
            # print(e.response)
            # if e.response["Error"]['Code'] == 'InvalidPermission.Duplicate':
            #     print(e.response["Error"]["Message"])
            # logging.WARNING(e)
            pass
        except Exception as e:
            print(e)

    def revokeSecurityGroupIngress(self, **kwargs):
        try:
            data = self.client.revoke_security_group_ingress(**kwargs)
            return data
        except Exception as revoke_err:
            print(revoke_err)
    # def

if __name__ == '__main__':
    if len(sys.argv) == 2:
        if sys.argv[1] == 'get-ip':
            print(getWanIPs())
        if sys.argv[1] == 'updateCloudFlare':

            apiKey = "195fe85f74228c6650c99dbb1357ad3b75499"
            email = "weidezhu@oneroot.io"
            cloud = CloudFlare(apiKey=apiKey, email=email)


            logging.info( '[' + '=' * 80 + ']' + '\n')
            logging.info("Date : {}\n".format(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())))
            logging.info('Current office wan ips:\n')
            logging.info(getWanIPs())

            to_be_add = {
                "id" :"fd4cf2544ff946f9b6661be02580121e",
                "paused": False,
                "description":"allow_office",
                "expression": "{}".format(generate_expression())
            }
            #
            update_result = cloud.updateFirewallFilter(zone='dcex.world', description_name='allow_office', filter_content=to_be_add)
            if update_result['success']:
                logging.info(update_result)
            else:
                logging.error(update_result)
        if sys.argv[1] == 'list-aws-sg':

            aws = AWSSecurityGroup(
                region_name='ap-southeast-1',
                aws_access_key_id='AKIAJKL7S5VKB6F57QIQ',
                aws_secret_access_key='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')
            groups = aws.getSecurityGroupDescription([security_group_id['prod'], security_group_id['demo']])
            # print(type(groups))
            # for k,v in groups.items():
            #     print('*' * 30)
            #     print(k)
            #     print(v)

            for group in groups['SecurityGroups']:
                print('[' + '-' * 60 + ']')
                if group['VpcId'] == 'vpc-0c1e943a2b848b141':
                    print('Found group in demo VPC : {}'.format(group['VpcId']))
                if group['VpcId'] == 'vpc-b1d7fed6':
                    print('Found group in prod VPC : {}'.format(group['VpcId']))

                print('''
                VPC ID : {VpcId}
            Group Name : {GroupName}
              Group ID : {GroupId}
            Traffic In :
                FromPort ----> {InFromPort}
                Protocol ----> {InIpProtocol}
                IpRanges ----> {InIpRanges}
                  ToPort ----> {InToPort}
            Traffic Out:
                Protocol ----> {OutIpProtocol}
                IpRanges ----> {OutIpRanges}
                '''.format(VpcId=group['VpcId'],
                           GroupName=group['GroupName'],
                           GroupId=group['GroupId'],
                           InFromPort=group['IpPermissions'][0]['FromPort'],
                           InIpProtocol=group['IpPermissions'][0]['IpProtocol'],
                           InIpRanges=group['IpPermissions'][0]['IpRanges'],
                           InToPort=group['IpPermissions'][0]['ToPort'],
                           OutIpProtocol=group['IpPermissionsEgress'][0]['IpProtocol'],
                           OutIpRanges=group['IpPermissionsEgress'][0]['IpRanges'],

                      ))
        if sys.argv[1] == 'update-aws':
            existing_sources = []
            local_sources = getWanIPs()
            if len(local_sources) == 0:
                print('Did not get IP addresses from office firewall, please try again later')
                sys.exit(1000)
            # local_sources.append('10.0.0.100')
            print('=' * 80 + '\n')
            print('current office ip addresses : \n')
            for ip in local_sources:
                print(' ***************  {}  ***************'.format(ip))

            aws = AWSSecurityGroup(
                region_name='ap-southeast-1',
                aws_access_key_id='AKIAJKL7S5VKB6F57QIQ',
                aws_secret_access_key='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')
            groups = aws.getSecurityGroupDescription([security_group_id['prod'], security_group_id['demo']])
            print('=' * 80 + '\n')
            for group in groups['SecurityGroups']:
                print(group)
                print('\n')
                print('-' * 80 + '\n')
                print('Adding office ip sources to  security group {} : {}\n'.format(group['GroupName'],group['GroupId']))
                existing_sources = []

                ip_ranges = []
                for local_ip in local_sources:
                    ip_ranges.append({'CidrIp':local_ip + '/32'})
                    local_ip_with_prefix = {'CidrIp': '{}/32'.format(local_ip)}
                    if local_ip_with_prefix not in group['IpPermissions'][0]['IpRanges']:
                        logging.info('Adding {}'.format(local_ip))
                        # print(group['IpPermissions'])

                    # if local_ip not in existing_sources:
                    #     print('=========================')
                    #     print('Updating {} to security group'.format(local_ip, group['GroupName']))
                    #     print('=' * 80)
                        print('[+++] Adding {}'.format(local_ip + '/32'))
                        print({
                                                            'IpProtocol':group['IpPermissions'][0]['IpProtocol'],
                                                            'FromPort':group['IpPermissions'][0]['FromPort'],
                                                            'ToPort':group['IpPermissions'][0]['ToPort'],
                                                            'IpRanges':[{'CidrIp':'{}/32'.format(local_ip)}]
                                                            })

                        add_res = aws.addSecurityGroupIngress(GroupId=group['GroupId'],
                                                    IpPermissions=[{
                                                        'IpProtocol':group['IpPermissions'][0]['IpProtocol'],
                                                        'FromPort':group['IpPermissions'][0]['FromPort'],
                                                        'ToPort':group['IpPermissions'][0]['ToPort'],
                                                        'IpRanges':[{'CidrIp':'{}/32'.format(local_ip)}]
                                                        }])
                        print(add_res)

                    else:
                        print('[:::]Ignoring {}/32, Reason: already exists'.format(local_ip))
                        logging.info('Ignore {}'.format(local_ip))
                # print('Removing legacy')
            groups = aws.getSecurityGroupDescription([security_group_id['prod'], security_group_id['demo']])
            print('=' * 80 + '\n')
            for group in groups['SecurityGroups']:
                print(group)
                print('\n')
                print('-' * 80 + '\n')
                print('Removing legacy office ip sources from  security group {} : {}\n'.format(group['GroupName'], group['GroupId']))
                existing_sources = []
                for cidr_ip in group['IpPermissions'][0]['IpRanges']:

                    # print('************ {}'.format(cidr_ip['CidrIp'].split('/')[0]))
                    logging.info('checking {} in security group {}'.format(cidr_ip['CidrIp'], group['GroupName']))
                    if cidr_ip['CidrIp'].split('/')[0] not in local_sources:
                        print('[---] Removing  {}'.format(cidr_ip['CidrIp']))
                        logging.info('Removing {}'.format(cidr_ip['CidrIp']))
                        print({
                                                        'IpProtocol':group['IpPermissions'][0]['IpProtocol'],
                                                        'FromPort':group['IpPermissions'][0]['FromPort'],
                                                        'ToPort':group['IpPermissions'][0]['ToPort'],
                                                        'IpRanges':[{'CidrIp':'{}/32'.format(cidr_ip['CidrIp'])}]
                                                        })
                        remove_res = aws.revokeSecurityGroupIngress(GroupId=group['GroupId'],
                                                    IpPermissions=[{
                                                        'IpProtocol':group['IpPermissions'][0]['IpProtocol'],
                                                        'FromPort':group['IpPermissions'][0]['FromPort'],
                                                        'ToPort':group['IpPermissions'][0]['ToPort'],
                                                        'IpRanges':[{'CidrIp':'{}'.format(cidr_ip['CidrIp'])}]
                                                        }])
                        print(remove_res)
                    else:
                        logging.info('{} is in use'.format(cidr_ip['CidrIp']))
                        print('[:::] {} ignored, Reason : in use'.format(cidr_ip['CidrIp']))
                        print({
                                                        'IpProtocol':group['IpPermissions'][0]['IpProtocol'],
                                                        'FromPort':group['IpPermissions'][0]['FromPort'],
                                                        'ToPort':group['IpPermissions'][0]['ToPort'],
                                                        'IpRanges':[{'CidrIp':'{}/32'.format(cidr_ip['CidrIp'])}]
                                                        })
        if sys.argv[1] == 'help':
            usage()
    else:
        usage()
    # print(generate_expression())
    # print(getWanIPs())