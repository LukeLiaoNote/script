#!/usr/bin/env python3
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

logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt = '%a, %d %b %Y %H:%M:%S'
)

def get_ip():
    url = 'http://ip.cn'
    req=requests.get(url)
    ip=re.findall(r'\d+\.\d+\.\d+\.\d+',req.text)  
    return ip[0]

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
        #print(self.listFirewallFilters(zone)['result'])
        for _filter in self.listFirewallRules(zone)['result']:
            if _filter['description'] == filter_name:
                return _filter['filter']['id']
    def updateFirewallFilter(self, zone, description_name, filter_content):
        try:
            print('Updating {} in zone {}'.format(description_name, zone))
            print('Update data : ')
            print(filter_content)
            url = urljoin(self.baseURL, 'zones/{}/filters/{}'.format(self.getZoneIdByName(zone), self.getFirewallFilterIdByName(zone, description_name)))
            #url = urljoin(self.baseURL, 'zones/{}/filters/{}'.format(self.getZoneIdByName(zone),'06814ff4c50d4f86a950f00ec91e7f24' ))

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

if __name__ == '__main__':
    ip = get_ip()
    apiKey = "******"
    email = "*********"
    cloud = CloudFlare(apiKey=apiKey, email=email)
    #print(cloud.listFirewallRules(zone='derinow.io'))
    # print(cloud.getZoneIdByName(name='derinow.io'))
    # print(cloud.listFirewallFilters(zone='derinow.io'))
    # print(cloud.getFirewallRuleIdByDescription(zone='derinow.io',description='allow-test'))
    
    #print(cloud.getFirewallFilterIdByName(zone='derinow.io', filter_name='allow-test'))
    to_be_add = {
        "id" :"{}".format(cloud.getFirewallFilterIdByName(zone='derinow.io', filter_name='allow-test')),
        "paused": False,
        "description":"allow-test",
        "expression": "(ip.src eq {})".format(ip)
    }
    
    update_result = cloud.updateFirewallFilter(zone='derinow.io', description_name='allow-test', filter_content=to_be_add)

