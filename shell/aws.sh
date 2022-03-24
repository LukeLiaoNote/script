#!/bin/bash
# aws多账号切换凭证
# use:  echo "alias example='source ~/.aws/aws.sh example'" > .bash_profile && source !$
id=$1
if [ -z $id ];then
    echo 'please input $1'
    exit
fi

AWS_ACCESS_KEY_ID=`cat ~/.aws/credentials|grep -A 2 "\[$id\]"|grep aws_access_key_id |awk -F"=" '{print $2}'| tr -d ' '`
AWS_SECRET_ACCESS_KEY=`cat ~/.aws/credentials|grep -A 2 "\[$id\]"|grep aws_secret_access_key |awk -F"=" '{print $2}'| tr -d ' '`
AWS_DEFAULT_REGION="ap-southeast-1"

echo "[$id]"
echo "region = $AWS_DEFAULT_REGION"
echo "aws_access_key_id = $AWS_ACCESS_KEY_ID"
echo "aws_secret_access_key = $AWS_SECRET_ACCESS_KEY"

export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
export AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION