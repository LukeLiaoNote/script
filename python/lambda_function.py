# -*- coding:utf-8 -*-
import requests
import json
import os

tokenUrl = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"

corpid = os.getenv('corpid')
corpsecret = os.getenv('corpsecret')
agentid = int(os.getenv('agentid'))


def get_token():
    values = {'corpid': corpid, 'corpsecret': corpsecret}
    req = requests.post(tokenUrl, params=values)
    data = json.loads(req.text)
    return data["access_token"]

sendMsg = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token="

def send_msg(msg):
    url = sendMsg + get_token()
    print(url)
    values = """{"touser" : "@all",
      "msgtype":"text",
      "agentid":%d,
      "text":{
        "content": "%s"
      },
      "safe":"0"
      }""" %(agentid,msg) 
    print(values)
    requests.post(url, values)

def lambda_handler(event, context):
    Message = json.loads(event['Records'][0]['Sns']['Message'])
    AlarmName = Message['AlarmName']
    Timestamp = event['Records'][0]['Sns']['Timestamp']
    NewStateReason = json.loads(event['Records'][0]['Sns']['Message'])['NewStateReason']
    print (Message)
    msg = "********AWS平台告警********\n"+ \
          "告警项目:"+AlarmName  + "\n" \
          "时间:" + Timestamp +"\n" \
          "========================" + "\n" \
          "原因:" + NewStateReason
    msg = str(msg)
    msg = msg.encode('utf-8').decode('latin-1')
    print(msg)
    send_msg(msg)