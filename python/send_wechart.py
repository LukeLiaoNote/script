#!/usr/bin/python
#_*_coding:utf-8 _*_

import requests
import json
import sys
import json



class WeChatOfficial:


    def __init__(self,corpid,corpsecret):
        self.corpid = corpid
        self.corpsecret = corpsecret

    #获取微信公众号token 
    @property
    def getToken(self):
        getTokenUrl = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=%s&corpsecret=%s' %(self.corpid,self.corpsecret)
        print(getTokenUrl)
        req = requests.get(getTokenUrl)
        res = req.json()
        Token = res['access_token']
        return Token
    
    #定义发送消息的部门
    def dataMessage(self,toparty,agentid,message):
        return  {
            "touser":"@all",    
            "toparty":"%s" %(toparty),    #企业号中的部门id。
            "msgtype":"text", #消息类型。
            "agentid":"%s" %(agentid),    #企业号中的应用id。
            "text":{
                "content": "%s" %(message)
            },
            "safe":"0"
        } 
    #发送消息模块
    def sendMessage(self,toparty,agentid,message):
        try:
            MessageUrl = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s' %(self.getToken)
            dataMessage =  {
                "touser":"@all",    
                "toparty":"%d" %(toparty),    #企业号中的部门id。
                "msgtype":"text", #消息类型。
                "agentid":"%d" %(agentid),    #企业号中的应用id。
                "text":{
                    "content": "%s" %(message)
                },
                "safe":"0"
                } 
            
            # print(dataMessage)
            req = requests.post(MessageUrl,json.dumps(dataMessage))
            res = req.json()
            print(res)
        except Exception as e:
            print(e)

if __name__ == '__main__':
    corpid =  '*****'   
    corpsecret = '*******' 
    
    toparty = 1 
    agentid = 1000009
    message = str(sys.argv[1]) #gitlab stage

    WeChat = WeChatOfficial(corpid=corpid,corpsecret=corpsecret)
    WeChat.sendMessage(toparty,agentid,message)