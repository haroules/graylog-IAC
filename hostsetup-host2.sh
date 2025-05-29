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
curl -s -u $admintoken:token "${postheaders[@]}" -X POST -d @index_host2_default.json "${url}"/system/indices/index_sets?pretty=true
curl -s -u $admintoken:token "${postheaders[@]}" -X POST -d @index_host2_docker_general.json "${url}"/system/indices/index_sets?pretty=true
curl -s -u $admintoken:token "${postheaders[@]}" -X POST -d @index_host2_docker_graylog.json "${url}"/system/indices/index_sets?pretty=true
curl -s -u $admintoken:token "${postheaders[@]}" -X POST -d @index_host2_firewalld.json "${url}"/system/indices/index_sets?pretty=true
cd ../

echo .
echo "create inputs"
cd inputs
## replace node id in templates
export nodeid=$(curl -s -u $admintoken:token -H "Accept: application/json" -X GET "${url}"/system/cluster/node?pretty=true | jq -r '.node_id')
jq --arg id $nodeid '.node |= $id' input_host2_rsyslog.json > tmp.json && mv tmp.json input_host2_rsyslog.json
jq --arg id $nodeid '.node |= $id' input_host2_gelf.json > tmp.json && mv tmp.json input_host2_gelf.json
# create input from file
curl -s -u $admintoken:token "${postheaders[@]}" -X POST -d @input_host2_rsyslog.json "${url}"/system/inputs?pretty=true
curl -s -u $admintoken:token "${postheaders[@]}" -X POST -d @input_host2_gelf.json "${url}"/system/inputs?pretty=true

echo "add static fields"
export inputid=$(curl -s -u $admintoken:token "${getheaders[@]}" -X GET "${url}"/system/inputs?pretty=true | jq -r '.inputs[] | select(.title=="host2-rsyslog") | .id')
curl -s -u $admintoken:token "${postheaders[@]}" -X POST -d '{"value":"host2_rsyslog","key":"input"}' "${url}"/system/inputs/"${inputid}"/staticfields?pretty=true
export inputid=$(curl -s -u $admintoken:token "${getheaders[@]}" -X GET "${url}"/system/inputs?pretty=true | jq -r '.inputs[] | select(.title=="host2-gelf-docker") | .id')
curl -s -u $admintoken:token "${postheaders[@]}" -X POST -d '{"value":"host2_gelf_docker","key":"input"}' "${url}"/system/inputs/"${inputid}"/staticfields?pretty=true
cd ../

echo "add extractors"
cd extractors
export inputid=$(curl -s -u $admintoken:token "${getheaders[@]}" -X GET "${url}"/system/inputs?pretty=true | jq -r '.inputs[] | select(.title=="host2-rsyslog") | .id')
curl -s -u $admintoken:token "${postheaders[@]}" -X POST -d @xtrctr_host2_rsyslog_firewalld.json "${url}"/system/inputs/"${inputid}"/extractors?pretty=true
cd ../

echo "add and start streams"
cd streams
## replace index set id in template
export indexsetid=$(curl -s -u $admintoken:token "${getheaders[@]}" -X GET "${url}"/system/indices/index_sets/search?searchTitle=host2-default-index | jq -r '.index_sets[].id')
jq --arg id $indexsetid '.index_set_id |= $id' stream_host2_default.json > tmp.json && mv tmp.json stream_host2_default.json
export indexsetid=$(curl -s -u $admintoken:token "${getheaders[@]}" -X GET "${url}"/system/indices/index_sets/search?searchTitle=host2-firewalld-index | jq -r '.index_sets[].id')
jq --arg id $indexsetid '.index_set_id |= $id' stream_host2_firewalld.json > tmp.json && mv tmp.json stream_host2_firewalld.json
export indexsetid=$(curl -s -u $admintoken:token "${getheaders[@]}" -X GET "${url}"/system/indices/index_sets/search?searchTitle=host2-gelf-docker-general-index | jq -r '.index_sets[].id')
jq --arg id $indexsetid '.index_set_id |= $id' stream_host2_docker_general.json > tmp.json && mv tmp.json stream_host2_docker_general.json
export indexsetid=$(curl -s -u $admintoken:token "${getheaders[@]}" -X GET "${url}"/system/indices/index_sets/search?searchTitle=host2-gelf-docker-graylog-index | jq -r '.index_sets[].id')
jq --arg id $indexsetid '.index_set_id |= $id' stream_host2_docker_graylog.json > tmp.json && mv tmp.json stream_host2_docker_graylog.json

## create and start streams
curl -s -u $admintoken:token "${postheaders[@]}" -X POST -d @stream_host2_default.json "${url}"/streams?pretty=true
export streamid=$(curl -s -u $admintoken:token "${getheaders[@]}" -X GET "${url}"/streams | jq -r '.streams[] | select(.title=="host2-default-stream") | .id')
curl -s -u $admintoken:token "${postheaders[@]}" -X POST "${url}"/streams/"${streamid}"/resume

curl -s -u $admintoken:token "${postheaders[@]}" -X POST -d @stream_host2_firewalld.json "${url}"/streams?pretty=true
export streamid=$(curl -s -u $admintoken:token "${getheaders[@]}" -X GET "${url}"/streams | jq -r '.streams[] | select(.title=="host2-firewalld-stream") | .id')
curl -s -u $admintoken:token "${postheaders[@]}" -X POST "${url}"/streams/"${streamid}"/resume

curl -s -u $admintoken:token "${postheaders[@]}" -X POST -d @stream_host2_docker_general.json "${url}"/streams?pretty=true
export streamid=$(curl -s -u $admintoken:token "${getheaders[@]}" -X GET "${url}"/streams | jq -r '.streams[] | select(.title=="host2-gelf-docker-general-stream") | .id')
curl -s -u $admintoken:token "${postheaders[@]}" -X POST "${url}"/streams/"${streamid}"/resume

curl -s -u $admintoken:token "${postheaders[@]}" -X POST -d @stream_host2_docker_graylog.json "${url}"/streams?pretty=true
export streamid=$(curl -s -u $admintoken:token "${getheaders[@]}" -X GET "${url}"/streams | jq -r '.streams[] | select(.title=="host2-gelf-docker-graylog-stream") | .id')
curl -s -u $admintoken:token "${postheaders[@]}" -X POST "${url}"/streams/"${streamid}"/resume
cd ../

