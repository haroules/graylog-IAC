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
curl -s -u $admintoken:token "${postheaders[@]}" -X POST -d @index_host1_default.json "${url}"/system/indices/index_sets?pretty=true
curl -s -u $admintoken:token "${postheaders[@]}" -X POST -d @index_host1_UFW.json "${url}"/system/indices/index_sets?pretty=true
cd ../

echo .
echo "create inputs"
cd inputs
# replace node id in template
export nodeid=$(curl -s -u $admintoken:token -H "Accept: application/json" -X GET "${url}"/system/cluster/node?pretty=true | jq -r '.node_id')
jq --arg id $nodeid '.node |= $id' input_host1_rsyslog.json > tmp.json && mv tmp.json input_host1_rsyslog.json
# create input from file
curl -s -u $admintoken:token "${postheaders[@]}" -X POST -d @input_host1_rsyslog.json "${url}"/system/inputs?pretty=true

echo .
echo "add static field"
export inputid=$(curl -s -u $admintoken:token "${getheaders[@]}" -X GET "${url}"/system/inputs?pretty=true | jq -r '.inputs[] | select(.title=="host1") | .id')
curl -s -u $admintoken:token "${postheaders[@]}" -X POST -d '{"value":"host1","key":"input"}' "${url}"/system/inputs/"${inputid}"/staticfields?pretty=true
cd ../

echo "add and start streams"
cd streams
# create and start default stream
## replace index set id in template
export indexsetid=$(curl -s -u $admintoken:token "${getheaders[@]}" -X GET "${url}"/system/indices/index_sets/search?searchTitle=host1-default-index | jq -r '.index_sets[].id')
jq --arg id $indexsetid '.index_set_id |= $id' stream_host1_default.json > tmp.json && mv tmp.json stream_host1_default.json
## create stream
curl -s -u $admintoken:token "${postheaders[@]}" -X POST -d @stream_host1_default.json "${url}"/streams?pretty=true
## start stream
export streamid=$(curl -s -u $admintoken:token "${getheaders[@]}" -X GET "${url}"/streams | jq -r '.streams[] | select(.title=="host1-default-stream") | .id')
curl -s -u $admintoken:token "${postheaders[@]}" -X POST "${url}"/streams/"${streamid}"/resume

# create and start UFW stream
## replace index set id in template
export indexsetid=$(curl -s -u $admintoken:token "${getheaders[@]}" -X GET "${url}"/system/indices/index_sets/search?searchTitle=host1-UFW-index | jq -r '.index_sets[].id')
jq --arg id $indexsetid '.index_set_id |= $id' stream_host1_ufw.json > tmp.json && mv tmp.json stream_host1_ufw.json
## create stream
curl -s -u $admintoken:token "${postheaders[@]}" -X POST -d @stream_host1_ufw.json "${url}"/streams?pretty=true
## start stream
export streamid=$(curl -s -u $admintoken:token "${getheaders[@]}" -X GET "${url}"/streams | jq -r '.streams[] | select(.title=="host1-ufw-stream") | .id')
curl -s -u $admintoken:token "${postheaders[@]}" -X POST "${url}"/streams/"${streamid}"/resume
cd ../