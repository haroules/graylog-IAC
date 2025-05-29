#!/bin/bash

usage() {
  echo "Usage: $0 -t <token> -u <url>"
  exit 1
}

admintoken=""
url=""

while getopts "t:u:" argument; do
    case ${argument} in
        t)
            admintoken=$OPTARG ;;
        u)
            url=$OPTARG ;;
        :)
            echo "Option -$OPTARG requires an argument" >&2
            usage ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            usage ;;
        *) 
            echo "Invalid option: -$OPTARG" >&2
            usage ;;
    esac
done    

if [ -z $admintoken ] || [ -z $url ];
then
    echo "Token and URL are required" >&2
    usage
fi

export admintoken
export url
export postheaders=(-H "Accept: application/json" -H "Content-Type: application/json" -H "X-Requested-By: XMLHttpRequest")
export getheaders=(-H "Accept: application/json")

echo "create indices"
cd indices
curl -s -u $admintoken:token "${postheaders[@]}" -X POST -d @index_firewall_default.json "${url}"/system/indices/index_sets?pretty=true
curl -s -u $admintoken:token "${postheaders[@]}" -X POST -d @index_firewall_filterlog.json "${url}"/system/indices/index_sets?pretty=true
cd ../

echo .
echo "create inputs"
cd inputs
# replace node id in template
export nodeid=$(curl -s -u $admintoken:token -H "Accept: application/json" -X GET "${url}"/system/cluster/node?pretty=true | jq -r '.node_id')
jq --arg id $nodeid '.node |= $id' input_firewall_rsyslog.json > tmp.json && mv tmp.json input_firewall_rsyslog.json
# create input from file
curl -s -u $admintoken:token "${postheaders[@]}" -X POST -d @input_firewall_rsyslog.json "${url}"/system/inputs?pretty=true

echo "add static field"
export inputid=$(curl -s -u $admintoken:token "${getheaders[@]}" -X GET "${url}"/system/inputs?pretty=true | jq -r '.inputs[] | select(.title=="firewall-rsyslog-udp") | .id')
curl -s -u $admintoken:token "${postheaders[@]}" -X POST -d '{"value":"firewall","key":"input"}' "${url}"/system/inputs/"${inputid}"/staticfields?pretty=true
cd ../

echo "add extractors"
cd extractors
curl -s -u $admintoken:token "${postheaders[@]}" -X POST -d @xtrctr_firewall_rsyslog_udp_ipcommon.json "${url}"/system/inputs/"${inputid}"/extractors?pretty=true
curl -s -u $admintoken:token "${postheaders[@]}" -X POST -d @xtrctr_firewall_rsyslog_udp_ipdata.json "${url}"/system/inputs/"${inputid}"/extractors?pretty=true
curl -s -u $admintoken:token "${postheaders[@]}" -X POST -d @xtrctr_firewall_rsyslog_udp_ipspecific.json "${url}"/system/inputs/"${inputid}"/extractors?pretty=true
curl -s -u $admintoken:token "${postheaders[@]}" -X POST -d @xtrctr_firewall_rsyslog_udp_ipv4specific.json "${url}"/system/inputs/"${inputid}"/extractors?pretty=true
curl -s -u $admintoken:token "${postheaders[@]}" -X POST -d @xtrctr_firewall_rsyslog_udp_tcpdata.json "${url}"/system/inputs/"${inputid}"/extractors?pretty=true
curl -s -u $admintoken:token "${postheaders[@]}" -X POST -d @xtrctr_firewall_rsyslog_udp_udpdata.json "${url}"/system/inputs/"${inputid}"/extractors?pretty=true
cd ../

echo "add and start streams"
cd streams
# create and start firewall-default-stream
## replace index set id in template
export indexsetid=$(curl -s -u $admintoken:token "${getheaders[@]}" -X GET "${url}"/system/indices/index_sets/search?searchTitle=firewall-default-index | jq -r '.index_sets[].id')
jq --arg id $indexsetid '.index_set_id |= $id' stream_firewall_default.json > tmp.json && mv tmp.json stream_firewall_default.json
## create stream
curl -s -u $admintoken:token "${postheaders[@]}" -X POST -d @stream_firewall_default.json "${url}"/streams?pretty=true
## start stream
export streamid=$(curl -s -u $admintoken:token "${getheaders[@]}" -X GET "${url}"/streams | jq -r '.streams[] | select(.title=="firewall-default-stream") | .id')
curl -s -u $admintoken:token "${postheaders[@]}" -X POST "${url}"/streams/"${streamid}"/resume

# create and start firewall-filterlog-stream
## replace index set id in template
export indexsetid=$(curl -s -u $admintoken:token "${getheaders[@]}" -X GET "${url}"/system/indices/index_sets/search?searchTitle=firewall-filterlog-index | jq -r '.index_sets[].id')
jq --arg id $indexsetid '.index_set_id |= $id' stream_firewall_filterlog.json > tmp.json && mv tmp.json stream_firewall_filterlog.json
## create stream
curl -s -u $admintoken:token "${postheaders[@]}" -X POST -d @stream_firewall_filterlog.json "${url}"/streams?pretty=true
## start stream
export streamid=$(curl -s -u $admintoken:token "${getheaders[@]}" -X GET "${url}"/streams | jq -r '.streams[] | select(.title=="firewall-filterlog-stream") | .id')
curl -s -u $admintoken:token "${postheaders[@]}" -X POST "${url}"/streams/"${streamid}"/resume
cd ../