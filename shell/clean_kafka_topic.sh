#!/bin/bash
kafka_dir="/usr/local/kafka"
kafka_cluster="ip1:port,ip2:port,ip3:port"
topic_list=`./kafka-topics.sh --bootstrap-server $kafka_cluster --list`
ip_list=`echo $kafka_cluster |awk -F',' 'BEGIN{FS=":";RS=","}{print $1}'`

cd $kafka_dir/bin
for topic in $topic_list; do 
    ./kafka-topics.sh --bootstrap-server $kafka_cluster --delete --topic ${topic}; 
done

for i in $ip_list;do
    ssh deploy@$i "sudo sh -c 'rm -rf /tmp/kafka-logs/*'"
done
