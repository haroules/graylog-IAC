import sys
import validators
import requests
import json
import base64
from jqpy import jq

#TODO: Align with setup.py

# Define global variables
baseurl = ""
getheaders = ""
postheaders = ""

def parse_args():
    global getheaders
    global postheaders
    global baseurl
    # check 2 args passed, argv has script name as arg so total should be 3
    if (len(sys.argv) != 3):
        print("Error, script arguments.", len(sys.argv) - 1, "were passed.") 
        print("Expecting auth token and url in that order, arguments will be undergo minimal input validation")
        sys.exit(1)
    # check token is 52 characters
    if(len(sys.argv[1]) != 52): 
        print("Error: Arguments, token should be 52 alpha-numeric characters. Token length was:", len(sys.argv[1]) )
        sys.exit(1)
    # check token is alpha numeric characters only
    if( not (sys.argv[1].isalnum())):
        print("Error: Arguments, token should be 52 alpha-numeric characters. Token passed had non alphanumeric characters.")
        sys.exit(1)
    # check url has valid form
    match = validators.url(sys.argv[2])
    if(not(bool(match))):
        print("Error: Arguments, url appears malformed")
        sys.exit(1)
    # check url responds
    try:
        response = requests.head(sys.argv[2], timeout=5)
        if (response.status_code != 200):
            print("URL does not appear to respond.")
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        sys.exit(1)
    
    # passed checks set global vars
    admintoken = sys.argv[1]
    baseurl = sys.argv[2]
    credentials = f"{admintoken}:token"  # Use token as username and 'token' as password
    encoded_token = base64.b64encode(credentials.encode()).decode()  # Base64 encode in correct format
    getheaders = {
        "Authorization": f"Basic {encoded_token}",  
        "Content-Type": "application/json",
    }
    postheaders = {
        "Authorization": f"Basic {encoded_token}",  
        "Content-Type": "application/json",
        "X-Requested-By": "XMLHttpRequest",
    }

def test_api_token():
    # perform quick check that token is valid by getting cluster status
    try:
        response = requests.get(baseurl + "/cluster", headers=getheaders)  
        if(response.status_code != 200):
            print("Testing api token failed/ Response code:",response.status_code)
            sys.exit(1)
        else:
            print("Token authenticated cluster get lifecycle:", jq('.[].lifecycle',json.loads(response.text)))
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        sys.exit(1)

# Removes sublists of strings from a main list of strings.
def remove_sublists(main_list, sublists_to_remove):
    return [s for s in main_list if s not in sublists_to_remove]

# Remove streams
def remove_streams():
    response = ""  # string variable to hold initial python response object
    streamsurl = "" # string variable to hold list streams api endpoint
    deleteurl = "" # string variable to hold delete streams api endpoint
    streamname = "" # string variable to hold stream name from id
    streamsidlist = [] # list variable to hold all stream ids
    builtin_streamsidlist = [] # static list variable to hold ids for built in
    cleanlistids = [] # list variable containing id list without built in ids
    cleanlistnames = [] # list variable containing names list without built ins

    # get list of all stream ids
    # declare static list of built in stream ids
    # create new list of ids without built in ids
    # create new list of titles without built ins
    # iterate list deleting one at a time
    streamsurl = baseurl + "/streams" # get a list of all streams
    try:
        response = requests.get(streamsurl, headers=getheaders)
        response.raise_for_status()
        streamsidlist = jq('.streams[].id',json.loads(response.text))
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
    except ValueError as e:
        print(f"JSON decoding error: {e}")
    # delete streams but don't delete built in streams
    builtin_streamsidlist = ["000000000000000000000001","000000000000000000000002","000000000000000000000003"]
    cleanlistids = remove_sublists(streamsidlist,builtin_streamsidlist)
    if isinstance(cleanlistids, list):
            print(f"{len(cleanlistids)} Streams found")
    for id in cleanlistids:
        try:
            streamsurlname = baseurl + "/streams/" + id # get stream by id filter out name
            response = requests.get(streamsurlname, headers=getheaders)
            response.raise_for_status()
            streamname = jq('.title',json.loads(response.text))
            # returns list, convert to string and append to built in list of ids
            cleanlistnames.append("".join(streamname))
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
        except ValueError as e:
            print(f"JSON decoding error: {e}")      
    print(f"Removing Stream Ids {cleanlistids}")      
    print(f"Removing Stream Titles {cleanlistnames}")
    for id in cleanlistids:
        try:
            deleteurl = baseurl + "/streams/" + id
            response = requests.delete(deleteurl, headers=postheaders)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
        except ValueError as e:
            print(f"JSON decoding error: {e}")
        
def remove_inputs():
    response = ""  # string variable to hold initial python response object
    inputsurl = "" # string variable to hold list inputs api endpoint
    deleteurl = "" # string variable to hold delete inputs api endpoint
    inputsidlist = [] # list variable to hold all input ids
    inputsnamelist = [] # list variable to hold all input names

    # get list of all input ids
    # get list of all input titles
    # iterate list deleting one at a time
    inputsurl = baseurl + "/system/inputs"
    try:
        response = requests.get(inputsurl, headers=getheaders)
        response.raise_for_status()
        inputsidlist = jq('.inputs[].id',json.loads(response.text))
        inputsnamelist = jq('.inputs[].title',json.loads(response.text))
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
    except ValueError as e:
        print(f"JSON decoding error: {e}")
    if isinstance(inputsidlist, list):
        print(f"{len(inputsidlist)} Inputs found")    
    print(f"Removing Input Ids {inputsidlist}")
    print(f"Removing Input Titles {inputsnamelist}")
    for id in inputsidlist:
        try:
            deleteurl = baseurl + "/system/inputs/" + id
            response = requests.delete(deleteurl, headers=postheaders)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
        except ValueError as e:
            print(f"JSON decoding error: {e}")  

def remove_indexsets():
    response = ""  # string variable to hold initial python response object
    indexsetsurl = "" # string variable to hold list index_sets api endpoint
    deleteurl = "" # string variable to hold delete index_sets api endpoint
    getindexidurl = "" # string variable to hold get index_sets id by name api endpoint
    indexid = "" # string variable to hold json index_sets id
    indexsetname = "" # string variable to hold index_set name from id
    indexidlist = [] # list variable to hold all index_set ids
    builtin_indexidlist = [] # list variable to hold all builtin index_set ids
    builtin_indexnamelist = [] # static list variable to hold all builtin index_set names
    cleanlist = [] # list variable to hold index_set ids without builtin list
    cleanlistnames = [] # list variable containing names list without built ins

    # get a list of all index_set ids
    # declare static list of built in index_set names
    # create list of built in index_set ids
    # create new list of index set ids without built in ids
    # create new list of index set titles without built ins
    # iterate list deleting one at a time
    indexsetsurl = baseurl + "/system/indices/index_sets"
    try:
        response = requests.get(indexsetsurl, headers=getheaders)
        response.raise_for_status()
        indexidlist = jq('.index_sets[].id',json.loads(response.text))
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
    except ValueError as e:
        print(f"JSON decoding error: {e}")    
    # get id's of built in by name extract string append to new list
    builtin_indexnamelist = ["Default index set","Graylog Events","Graylog System Events"]
    for indexname in builtin_indexnamelist:
        try:
            getindexidurl = baseurl + "/system/indices/index_sets/search?searchTitle=" + indexname + "&skip=0&limit=0&stats=false"
            response = requests.get(getindexidurl, headers=getheaders)
            response.raise_for_status()
            indexid = jq('.index_sets[].id',json.loads(response.text))
            # returns list, convert to string and append to built in list of ids
            builtin_indexidlist.append("".join(indexid))
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
        except ValueError as e:
            print(f"JSON decoding error: {e}") 
    cleanlist = remove_sublists(indexidlist,builtin_indexidlist)
    if isinstance(cleanlist, list):
        print(f"{len(cleanlist)} Index Sets found")
    for id in cleanlist:
        try:
            indexseturlname = baseurl + "/system/indices/index_sets/" + id # get indexset by id filter out name
            response = requests.get(indexseturlname, headers=getheaders)
            response.raise_for_status()
            indexsetname = jq('.title',json.loads(response.text))
            # returns list, convert to string and append to built in list of ids
            cleanlistnames.append("".join(indexsetname))
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
        except ValueError as e:
            print(f"JSON decoding error: {e}")     
    print(f"Removing IndexSet Ids {cleanlist}")
    print(f"Removing IndexSet Titles {cleanlistnames}")
    for id in cleanlist:
        try:
            deleteurl = baseurl + "/system/indices/index_sets/" + id
            response = requests.delete(deleteurl, headers=postheaders)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
        except ValueError as e:
            print(f"JSON decoding error: {e}")  

def main():
    parse_args()
    test_api_token()
    remove_streams()
    remove_inputs()
    remove_indexsets()
    print("Done removing streams, inputs, and index sets")

main()