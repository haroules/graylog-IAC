# from pyenv
import sys
import base64
import os
import shutil
import json
import requests
from validators import url, ValidationError
from jqpy import jq

from typing import Union

# from source
import graylog_global_vars

def exit_with_message(message: str, error_code: int):
    # pass message exit with integer code to cut down on print followed by sys.exit
    print(message)
    sys.exit(error_code)

def is_json_valid(file_path: str) -> bool:
    # check if file exist and can load as json or throws error (return True/False)
    try:
        if(os.path.isfile(file_path)):
            with open(file_path, 'r') as f:
                data=json.load(f)
            if(isinstance(data,dict)):
                return True
        else:
            print(f"[ERROR] File doesn't exist {file_path}")
            return False
    except json.JSONDecodeError as e:
        print(f"[ERROR] There was a problem decoding json: {file_path}")
        return False

def contains_sublist(sub_list: list, main_list: list) -> bool:
    # simple check if second list contains first list as an item itself
    # return true if it does, false if not
    if( ( not(isinstance(sub_list,list)) ) or ( not(isinstance(main_list,list)) ) ):
        exit_with_message("[ERROR] One or more items passed to contains_sublist is not a list",1)
    int_len1 = 0
    int_len2 = 0
    # check if one list is subset of the other (return True/False)
    int_len1 = len(sub_list)
    int_len2 = len(main_list)
    for i in range(int_len2 - int_len1 + 1):
        if main_list[i:i + int_len1] == sub_list:
            return True
    return False

def check_graylog_baseurl(args: list) -> Union[str, bool]:
    print("Verify graylog baseurl.")
    
    match = url(args[2])  # check url has valid form
    if(not(bool(match))):
        return(f"[ERROR] URL appears malformed: {args[2]}")
    try:
        response = requests.get(args[2],timeout=5)  # check base url responds with no auth
        if (response.status_code == 200):
            try:
                responsetext=json.loads(response.text) # check output has a specific expexted response
                if not ("cluster_id" and "node_id" and "version" and "tagline" in responsetext):
                    return(f"[ERROR] {args[2]} Didn't provide expected response. Recieved:\n {response.text}")
            except json.JSONDecodeError as e:
                return(f"[ERROR] There was a problem decoding json response: {e}, URL: {args[2]}")
    except requests.exceptions.RequestException as e:
        return(f"[ERROR] {args[2]} Didn't respond.\n Error was: {e}")
    print("[Done] Verify graylog baseurl.\n")
    return True

def check_api_token(args: list) -> Union[str, bool]:
    # perform quick check that token is valid by getting cluster status
    # immediately exit if not status 200, otherwise print status of cluster
    print("Verify api token authenticates and cluster is up.")
    try:
        response = requests.get(args[0],headers=args[1],timeout=5)  
        if(response.status_code != 200):
            return(f"[ERROR] Testing api token failed. Response code:{response.status_code}")
        else:
            str_lifecycle_status = jq('.[].lifecycle',json.loads(response.text),raw_output=True).text.strip('"')
            if(str_lifecycle_status == "running"):
                print("[Done] Token authenticated to cluster and cluster is up.\n")
                return(True)
            else:
                return(f"[ERROR] cluster status is not ok. Status:{str_lifecycle_status}")
    except requests.exceptions.RequestException as e:
        return(f"[ERROR]  Request error: {e}")
    except json.JSONDecodeError as e:
        return(f"There was a problem decoding json: {e}")
    except Exception as e:
        return(f"[ERROR] Unknown error occurred: {e}")

def set_global_vars(args: list):
    # see global_vars for description of each var
    print("Assigning global variables.")
    
    # based on positional arguments we have to set cur working directory and verbose flag appropriately
    if(len(args)==4):
        graylog_global_vars.bool_verbose = True # default to verbose if no argument supplied otherwise
        str_pth_cwd = args[3]
    elif(len(args)==5):
        graylog_global_vars.bool_verbose = args[3]
        str_pth_cwd = args[4]
    # set static values for urls
    graylog_global_vars.str_inputs_url = args[2] + "/system/inputs" 
    graylog_global_vars.str_indexsets_url = args[2] + "/system/indices/index_sets" 
    graylog_global_vars.str_node_id_url = args[2] + "/system/cluster/node"
    graylog_global_vars.str_streams_url = args[2] + "/streams"
    graylog_global_vars.str_cluster_url = args[2] + "/cluster"
    # set static values for directories
    graylog_global_vars.str_pth_host_cfg_dir = str_pth_cwd + "/host-configs" 
    graylog_global_vars.str_pth_host_cfg_template = str_pth_cwd + "/host-config-templates" 
    graylog_global_vars.str_pth_extrctr_cfg = str_pth_cwd + "/extractors" 
    graylog_global_vars.str_pth_indices_cfg = str_pth_cwd + "/indices" 
    graylog_global_vars.str_pth_inputs_cfg = str_pth_cwd + "/inputs" 
    graylog_global_vars.str_pth_streams_cfg = str_pth_cwd + "/streams" 
    graylog_global_vars.str_pth_schemas = str_pth_cwd + "/schemas"
    # set static values for filenames
    graylog_global_vars.str_pth_host_schema = graylog_global_vars.str_pth_schemas + "/schema_host.json" 
    graylog_global_vars.str_pth_schema_index = graylog_global_vars.str_pth_schemas + "/schema_index.json"  
    graylog_global_vars.str_pth_schema_input = graylog_global_vars.str_pth_schemas + "/schema_input.json"
    graylog_global_vars.str_pth_schema_extractor = graylog_global_vars.str_pth_schemas + "/schema_extractor.json" 
    graylog_global_vars.str_pth_schema_stream = graylog_global_vars.str_pth_schemas + "/schema_stream.json"
    # list of paths to all important data directories used in:
    # graylog_verify::verify_configfiles_filesystem
    # graylog_helpers::make_config_backup
    graylog_global_vars.list_config_directories = [ 
        graylog_global_vars.str_pth_host_cfg_dir, graylog_global_vars.str_pth_host_cfg_template, 
        graylog_global_vars.str_pth_extrctr_cfg, graylog_global_vars.str_pth_indices_cfg, 
        graylog_global_vars.str_pth_inputs_cfg, graylog_global_vars.str_pth_streams_cfg, 
        graylog_global_vars.str_pth_schemas 
    ]
    # set tokens and headers dictionaries
    credentials = f"{args[1]}:token"  # Use input token as username and string 'token' as password
    encoded_token = base64.b64encode(credentials.encode()).decode()  # Base64 encode token as required to pass it
    graylog_global_vars.dict_get_headers = {
        "Authorization": f"Basic {encoded_token}",  
        "Content-Type": "application/json",
    }
    graylog_global_vars.dict_post_headers = {
        "Authorization": f"Basic {encoded_token}",  
        "Content-Type": "application/json",
        "X-Requested-By": "XMLHttpRequest",
    }
    print("[Done] Assigning global variables.\n")





    