#!/bin/bash
#deployment资源-->获取RS资源-->查看RS状态 --> 输出结果
RESOURCE_TYPE=$1
RESOURCE_NAME=$2
NAMESPACE=$3
# 将传入的名称大写
RESOURCE_TYPE_UP=$(echo ${RESOURCE_TYPE} | tr '[a-z]' '[A-Z]')

# 判断控制资源类型
if [[ ${RESOURCE_TYPE_UP} =~ "DEPLOYMENT" ]]
then
    RESOURCE_TYPE=deployment
else
    RESOURCE_TYPE=deamonset
fi


#echo $RESOURCE_TYPE

function get_rs_id() {
    RESOURCE_TYPE=$1
    RESOURCE_NAME=$2
    NAMESPACE=$3

    OldRS=`kubectl describe ${RESOURCE_TYPE} ${RESOURCE_NAME} -n ${NAMESPACE}|grep -E  "^OldReplicaSets"`
    if [[ ${OldRS} =~ "none" ]];then
        echo 100
    else 
        NewRS=`kubectl describe ${RESOURCE_TYPE} ${RESOURCE_NAME} -n ${NAMESPACE}|grep  -E "^NewReplicaSet"`
        NewRsID="$(echo -e ${NewRS}|awk '{print $2}')"
       echo $NewRsID
    fi
}


function get_rs_status() {
   ReplicaSetId=$1
   NAMESPACE=$2
   RS_STATUS=`kubectl get rs ${ReplicaSetId} -n ${NAMESPACE}|grep  "${ReplicaSetId}" `
   #RS_STATUS=`kubectl get rs ${ReplicaSetId} -n ${NAMESPACE}|awk -F "NAME DESIRED CURRENT READY AGE" '{print $2}'`
   echo $RS_STATUS
}

function get_rs_events() {
   ReplicaSetId=$1
   NAMESPACE=$2
   kubectl get events -n $NAMESPACE --sort-by='.metadata.creationTimestamp'|grep ${ReplicaSetId}
}
# RS=`get_rs_id ${RESOURCE_TYPE} ${RESOURCE_NAME} ms`
# echo $RS
# RS_STATUS=`get_rs_status $RS ms`
# RS_NAME=`echo -e ${RS_STATUS}| cut -d " " -f 1`
# RS_DESIRED=`echo -e ${RS_STATUS}| cut -d " " -f 2`
# RS_CURRENT=`echo -e ${RS_STATUS}| cut -d " " -f 3`
# RS_READY=`echo -e ${RS_STATUS}| cut -d " " -f 4`
# RS_AGE=`echo -e ${RS_STATUS}| cut -d " " -f 5`
# echo $RS_AGE
# printf "NAME:%-40s DESIRED:%-10s CURRENT:%-10s READY:%-10s AGE:%-20s\n" $RS_NAME $RS_DESIRED $RS_CURRENT $RS_READY $RS_AGE

function check_main(){
    RESOURCE_TYPE=$1
    RESOURCE_NAME=$2
    NAMESPACE=$3
    #检测间隔时间 秒
    TIMEOUT=10
    #检测周期
    PERIOD=6
    RS=`get_rs_id ${RESOURCE_TYPE} ${RESOURCE_NAME} ${NAMESPACE}`
    if [[ $RS == 100 ]];then
        echo "此次发布版本与线上运行版本一致，跳过健康检查，请确认此次发布应用的commit版本号是否为您期望发布的版本！"
        exit 0
    fi
    check_status="NO"
    for((i=1;i<=$PERIOD;i++));  
    do   
        RS_STATUS=`get_rs_status $RS $NAMESPACE`
        RS_NAME=`echo -e ${RS_STATUS}| cut -d " " -f 1`
        RS_DESIRED=`echo -e ${RS_STATUS}| cut -d " " -f 2`
        RS_CURRENT=`echo -e ${RS_STATUS}| cut -d " " -f 3`
        RS_READY=`echo -e ${RS_STATUS}| cut -d " " -f 4`
        RS_AGE=`echo -e ${RS_STATUS}| cut -d " " -f 5`
        ((USETIME=($TIMEOUT*$PERIOD)/60))
        echo "开始对应用的部署状态进行监控，整个过程将花费$USETIME分钟，请耐心等待～"
        echo -e "第 ${i} 次健康检查"
        sleep $TIMEOUT
        # if [[ $i == 1 ]];then
        #     sleep 30 
        # else
        #     sleep 60
        # fi
        printf "NAME:%-40s DESIRED:%-10s CURRENT:%-10s READY:%-10s AGE:%-20s\n" $RS_NAME $RS_DESIRED $RS_CURRENT $RS_READY $RS_AGE
        if [[ ${RS_DESIRED} == ${RS_READY} ]];then
            echo -e "第 ${i} 次健康检查结果: 通过"
            check_status="YES"
        else
            echo -e "第 ${i} 次健康检查结果: 失败" 
            if [[ $i != 1 ]]  && [[ ${check_status} == "YES" ]] ;then
                echo "RS状态由健康转为不健康,程序未运行成功,请登陆日志服务器查看日志！"
                get_rs_events  $RS $NAMESPACE
                exit 2
            fi
        fi
    done  
    if [[ ${check_status} == "YES" ]];then
        echo "健康检查通过，新版应用已发布上线"
    else
        echo "健康检查未通过,请登陆日志服务器查看日志！"
        get_rs_events  $RS $NAMESPACE 
        exit 2
    fi
}
check_main $RESOURCE_TYPE $RESOURCE_NAME $NAMESPACE
