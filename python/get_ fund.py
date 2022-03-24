# -*- coding:utf-8 -*-

import requests,json,time
from dingtalkchatbot.chatbot import DingtalkChatbot
import re
import pandas as pd
import collections 

pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)

#获取时间戳
def GetTime():
    t = time.time()
    Timestamp = round(t * 1000)
    # print(Timestamp)
    return Timestamp

#传入大盘指数新浪接口
def MarketIndex(SharesID):
    MarketList = []
    Headers = {'content-type':'application/json','User-Agent': 'Apache-HttpClient/4.5.2 (Java/1.8.0_102)'}
    sinajs = "http://hq.sinajs.cn/list=s_" + str(SharesID)
    Msg = requests.get(sinajs, headers=Headers)
    SharesMsg =  Msg.text
    #print(SharesMsg)
    if SharesID in SharesMsg:
        GetSharesName = SharesMsg.split(",")[0].split("=")[1].split("\"")[1]
        SharesTotal = SharesMsg.split(",")[1]
        Gain = SharesMsg.split(",")[2]
        GainPercent = SharesMsg.split(",")[3]
        GetMarketMsg =  GetSharesName + ":"  + SharesTotal + " 涨跌幅:" + str(Gain) + "  涨跌幅率:" +  str(GainPercent) + "%"
    return GetMarketMsg

#传入基金代码和当天时间戳获取当前数据
def GetFundData(fundId,GetTimestamp):
    Headers = {'content-type':'application/json','User-Agent': 'Apache-HttpClient/4.5.2 (Java/1.8.0_102)'}
    TTurl = "http://fundgz.1234567.com.cn/js/" + str(fundId) +  ".js?rt=" + str(GetTimestamp)
    r = requests.get(TTurl, headers=Headers)
    GetMsg = r.text
    FmtMsg = json.loads(re.match(".*?({.*}).*", GetMsg, re.S).group(1))
    FmtMsg['基金代码'] = FmtMsg.pop("fundcode")
    FmtMsg['基金名称'] = FmtMsg.pop("name")
    FmtMsg['估值时间'] = FmtMsg.pop("gztime")
    FmtMsg['结算日期'] = FmtMsg.pop("jzrq")
    FmtMsg['单位净值'] = FmtMsg.pop("dwjz")
    FmtMsg['估算净值'] = FmtMsg.pop("gsz")
    FmtMsg['涨幅'] = FmtMsg.pop("gszzl") + "%"

    # FmtMsg['test'] = FmtMsg.pop['fundcode']
    return FmtMsg

def machine_cost(paylist,now,poundage):
    now = float(now)
    total = 0
    share = 0
    really_total = 0 
    for i in paylist:
        share = share + (paylist[i]* ( 1 - poundage )/i)
        total = total + (paylist[i] * ( 1 - poundage ))
        really_total = really_total + paylist[i]
    # print (total)
    # print (share)
    # print (really_total)
    cost = total / share
    earning = ((now - cost) * share) - (really_total * poundage)
    earning_rate = str((earning / really_total)*100) + "%"
    footings = total + earning
    state = {'成本':cost,'收益':earning,'收益率':earning_rate,'结算金额':footings}
    return state

if __name__ ==  '__main__':
    fundIdList = {
        "200006":{
            "paylist":{1.4945:2000,1.5281:2000},
            "poundage":0.0012
        },
        "519193":{
            "paylist":{2.3247:2000,2.3578:2000},
            "poundage":0.0015
        }
    }
    GetTimestamp = GetTime()
    earn = 0 
    footings = 0
    status_list = []
    GetData_list = []
    for fundId in fundIdList:
        GetData = GetFundData(fundId,GetTimestamp)
        pay_list = fundIdList[fundId]['paylist']
        now = GetData['估算净值']
        poundage = fundIdList[fundId]['poundage']
        status = machine_cost(pay_list,now,poundage)
        status['基金名称'] = GetData['基金名称'] 
        earn = earn + status['收益']
        footings = footings + status['结算金额']
        status = collections.OrderedDict(status)
        status.move_to_end('基金名称',last=False)
        status_list.append(status)
        GetData_list.append(GetData)
    status_pd = pd.DataFrame.from_dict(status_list)
    GetData_pd = pd.DataFrame.from_dict(GetData_list)
    print(GetData_pd)
    print(status_pd)
    print("目前总收益:{}".format(earn))
    print("目前总金额:{}".format(footings))
    print(MarketIndex('sh000001'))