# Examples of how to run some common REST API endpoints

## Setup: get admin token from Web UI (Show Profile, Edit Tokens) and export as variables
**modify to match your IP or fqdn for the URL**
```
# space at the beginning ensures it doesn't go into shell history
 export admintoken=<token goes here>
export url=http://192.168.1.2:9000/api/
export postheaders=(-H "Accept: application/json" -H "Content-Type: application/json" -H "X-Requested-By: XMLHttpRequest")
export getheaders=(-H "Accept: application/json")
```

## Get cluster status
```
curl -u $admintoken:token "${getheaders[@]}" -X GET "${url}"cluster?pretty=true
```
## index related
1. Get all indices
```
curl -u $admintoken:token "${getheaders[@]}" -X GET "${url}"system/indices/index_sets?pretty=true
```
2. Get specific index
```
curl -u $admintoken:token "${getheaders[@]}" -X GET "${url}"system/indices/index_sets/search?searchTitle=firewall
```
3. Get specific index id 
```
curl -s -u $admintoken:token "${getheaders[@]}" -X GET "${url}"system/indices/index_sets/search?searchTitle=host1 | jq -r '.index_sets[].id'
```
4. Rebuild/sync index range
```
curl -u $admintoken:token "${postheaders[@]}" -X POST "${url}"system/indices/ranges/rebuild
```
## Inputs related
1. Get all inputs
```
curl -s -u $admintoken:token "${getheaders[@]}" -X GET "${url}"system/inputs?pretty=true
```
2. Get specific input id
```
curl -s -u $admintoken:token "${getheaders[@]}" -X GET "${url}"system/inputs?pretty=true | jq -r '.inputs[] | select(.title=="host1") | .id'
```
3. Get specific input complete config
```
curl -s -u $admintoken:token "${getheaders[@]}" -X GET "${url}"system/inputs/{inputid}?pretty=true
```
4. Get list of all input types to generate local schema files
```
curl -s -u $admintoken:token "${getheaders[@]}" -X GET "${url}"system/inputs/types?pretty=true
```
5. Get specific input type definition
```
curl -s -u $admintoken:token "${getheaders[@]}" -X GET "${url}"system/inputs/types/org.graylog2.inputs.syslog.udp.SyslogUDPInput?pretty=true
```

## Streams related
1. Get all streams
```
curl -u $admintoken:token "${getheaders[@]}" -X GET "${url}"streams?pretty=true
```


