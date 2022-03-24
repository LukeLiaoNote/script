import requests,json
import boto3

## 获取access token
def GetJumpserverToken(username,password):
    post_data  = {'username':username,'password':password}
    url = 'https://example.com/api/v1/authentication/auth/'
    req = requests.post(url,data=post_data)
    token = req.json()
    Authorization = token["keyword"] + " "+ token["token"]
    return  Authorization

## 获取资产信息
def GetAssetIds(token):
    Authorization = {'Authorization': token}
    #url = 'https://example.com/api/v1/assets/assets/'
    url = 'https://example.com/api/assets/v1/assets/'
    assetList = {}
    payload = {"all": "all"}
    req = requests.get(url, headers=Authorization, params=payload)
    res = req.json()
    print(res)
    for i in res:
        asset = {str(i['hostname']):i['ip']}
        assetList.update(asset)
    return assetList

def ModifyAssetInfo(token,bulkData):
    Authorization = {'Authorization': token,'content-type': 'application/json'}
    url = 'https://example.com/api/v1/assets/assets/'
    try:
        req = requests.post(url, headers=Authorization, data=bulkData)
        res = req.json()
        return res
    except requests.exceptions.HTTPError:
        print('HTTPError')


### 获取aws 上运行机器的内网ip跟 instance_id
def GetAwsInstancesInfo():
    instanceList = {}
    ec2 = boto3.client('ec2',aws_access_key_id='*',aws_secret_access_key='*****',region_name='ap-southeast-1')

    #只返回运行的机器
    instanceid_filter = {'Name': 'instance-state-name', 'Values': ['running']}
    response = ec2.describe_instances(Filters=[instanceid_filter])
    #print(response)
    for i in response['Reservations']:
        for key in i['Instances']:
            for j in key['Tags']:
                if j['Key'] == 'Name':
                    ec2_name = j['Value']
            instances = {key['InstanceId']: [key['PrivateIpAddress'],ec2_name]}
            instanceList.update(instances)
    return instanceList

### 比较需要修改的数据得出json数据
def CompareAwsAndJumpserver(awsInstaceList, jumpserverAssets,node_id,user_id):
    modifyLists = []
    for i in awsInstaceList:
        if awsInstaceList[i][0] not in jumpserverAssets.values():
            print('该实例不存在跳板机中 机器名:',awsInstaceList[i][1],'instance_id:',i ,'ip:',awsInstaceList[i][0])
            modifydict = {
                "ip": awsInstaceList[i][0],
                "hostname": awsInstaceList[i][1],
                "number": i,
                "port": 22,
                "is_active": '1',
                "platform": 'Linux',
                "admin_user": user_id,
                "nodes": [
                    node_id
                ]
            }
            modifyLists.append(modifydict)
            #modifydicts = json.dumps(modifydicts)
    return modifyLists

##获取jumpserver节点id
def Getnode_id(token,node):
    Authorization = {'Authorization': token}
    payload = {"value": node}
    url = 'https://example.com/api/v1/assets/nodes/'
    req = requests.get(url, headers=Authorization, params=payload)
    res = req.json()
    node_id=res[0]['id']
    return node_id

##获取jumpserver系统用户id
def Getuser_id(token,user):
    Authorization = {'Authorization': token}
    payload = {'username': user}
    url = 'https://example.com/api/v1/assets/admin-users'
    req = requests.get(url, headers=Authorization, params=payload)
    res = req.json()
    user_id=res[0]['id']
    return user_id

if __name__ == '__main__':
    username = '***'   #jumpserver username
    password = '***'   #jumpserver password
    node = 'rsync-aws'  #jumpserver供同步所使用节点名
    user = 'ec2-user'  #jumpserver系统用户
    token=GetJumpserverToken(username, password) 	#获取token
    jumpserverAssets = GetAssetIds(token)
    awsInstanceList = GetAwsInstancesInfo()
    node_id = Getnode_id(token,node)
    # user_id = Getuser_id(token,user)
    user_id = '27b5d738-f0b0-4577-8858-6d3858d2fdb2'
    # print("jumpserverAssets:{}".format(jumpserverAssets))
    # print("--------------")
    # print("awsInstanceList:{}".format(awsInstanceList))
    changeJumpserList = CompareAwsAndJumpserver(awsInstanceList, jumpserverAssets,node_id, user_id)
    for i in changeJumpserList:
        i_data = json.dumps(i)
        aa = ModifyAssetInfo(token,i_data)
        print(aa)
        
