# from pyenv
import sys
import base64
import os
import shutil
import json
import requests
from jqpy import jq
from datetime import datetime

# from source
import graylog_global_vars

def exit_with_message(message: str, error_code: int):
    # pass message exit with integer code to cut down on print followed by sys.exit
    print(message)
    sys.exit(error_code)

def is_json_valid(file_path: str) -> bool:
    # check if file is json or throws error (return True/False)
    try:
        with open(file_path, 'r') as f:
            json.load(f)
        return True
    except json.JSONDecodeError as e:
        print(f"There was a problem decoding json: {e}")
        return False

def contains_sublist(sub_list: list, main_list: list) -> bool:
    # simple check if second list contains first list as an item itself
    # return true if it does, false if not
    int_len1 = 0
    int_len2 = 0
    # check if one list is subset of the other (return True/False)
    int_len1 = len(sub_list)
    int_len2 = len(main_list)
    for i in range(int_len2 - int_len1 + 1):
        if main_list[i:i + int_len1] == sub_list:
            return True
    return False

def check_graylog_baseurl():
     # check base url responds with no auth
    print("Verify graylog baseurl appears valid.")
    try:
        response = requests.get(sys.argv[2],timeout=5)
        if (response.status_code == 200):
            try:
                responsetext=json.loads(response.text)
                if not ("cluster_id" and "node_id" and "version" and "tagline" in responsetext):
                    exit_with_message(f"[ERROR] {sys.argv[2]} Didn't provide expected response. Recieved:\n {response.text}",1)
            except Exception as e:
                exit_with_message(f"[Error] Not a json response: {e}",1)
    except requests.exceptions.RequestException as e:
        exit_with_message(f"[ERROR] {sys.argv[2]} Didn't respond.\n Error was: {e}",1)
    print("[Done] Verify graylog baseurl.\n")

def test_api_token():
    # perform quick check that token is valid by getting cluster status
    # immediately exit if not status 200, otherwise print status of cluster
    print("Verify api token authenticates and cluster is up.")
    try:
        response = requests.get(graylog_global_vars.str_cluster_url, headers=graylog_global_vars.dict_get_headers)  
        if(response.status_code != 200):
            #print("[Error] Testing api token failed. Response code:",response.status_code)
            #sys.exit(1)
            exit_with_message(f"[Error] Testing api token failed. Response code:,{response.status_code}")
        else:
            str_lifecycle_status = jq('.[].lifecycle',json.loads(response.text),raw_output=True).text.strip('"')
            if(str_lifecycle_status == "running"):
                print("[Done] Token authenticated to cluster and cluster is up.\n")
            else:
                exit_with_message("[Error] cluster status is not ok",1)
    except requests.exceptions.RequestException as e:
        print(f"[Error]  Request error: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"There was a problem decoding json: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[Error] Unknown error occurred: {e}")
        sys.exit(1)

def set_global_vars():
    # see global_vars for description of each var
    print("Assigning global variables.")
    # set static values for urls
    graylog_global_vars.str_inputs_url = graylog_global_vars.str_graylogbase_url + "/system/inputs" 
    graylog_global_vars.str_indexsets_url = graylog_global_vars.str_graylogbase_url + "/system/indices/index_sets" 
    graylog_global_vars.str_node_id_url = graylog_global_vars.str_graylogbase_url + "/system/cluster/node"
    graylog_global_vars.str_streams_url = graylog_global_vars.str_graylogbase_url + "/streams"
    graylog_global_vars.str_cluster_url = graylog_global_vars.str_graylogbase_url + "/cluster"
    # set static values for directories
    graylog_global_vars.str_pth_host_cfg_dir = graylog_global_vars.str_pth_cwd + "/host-configs" 
    graylog_global_vars.str_pth_host_cfg_template = graylog_global_vars.str_pth_cwd + "/host-config-templates" 
    graylog_global_vars.str_pth_extrctr_cfg = graylog_global_vars.str_pth_cwd + "/extractors" 
    graylog_global_vars.str_pth_indices_cfg = graylog_global_vars.str_pth_cwd + "/indices" 
    graylog_global_vars.str_pth_inputs_cfg = graylog_global_vars.str_pth_cwd + "/inputs" 
    graylog_global_vars.str_pth_streams_cfg = graylog_global_vars.str_pth_cwd + "/streams" 
    graylog_global_vars.str_pth_schemas = graylog_global_vars.str_pth_cwd + "/schemas"
    # set static values for filenames
    graylog_global_vars.str_pth_host_schema = graylog_global_vars.str_pth_schemas + "/schema_host.json" 
    graylog_global_vars.str_pth_schema_index = graylog_global_vars.str_pth_schemas + "/schema_index.json"  
    graylog_global_vars.str_pth_schema_input = graylog_global_vars.str_pth_schemas + "/schema_input.json"
    graylog_global_vars.str_pth_schema_extractor = graylog_global_vars.str_pth_schemas + "/schema_extractor.json" 
    graylog_global_vars.str_pth_schema_stream = graylog_global_vars.str_pth_schemas + "/schema_stream.json"
    # list of paths to all important data directories
    graylog_global_vars.list_config_directories = [ 
        graylog_global_vars.str_pth_host_cfg_dir, graylog_global_vars.str_pth_host_cfg_template, 
        graylog_global_vars.str_pth_extrctr_cfg, graylog_global_vars.str_pth_indices_cfg, 
        graylog_global_vars.str_pth_inputs_cfg, graylog_global_vars.str_pth_streams_cfg, 
        graylog_global_vars.str_pth_schemas 
    ]

    # set tokens and headers dictionaries
    credentials = f"{graylog_global_vars.str_admintoken}:token"  # Use input token as username and string 'token' as password
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

def make_config_backup():
    # make a clean backup copy of all config objects that may get overwritten 
    # with nodeid, or indexid, or may just get messed up (point in time)
    # create timestamp and store as formatted string
    # create backup folder name incorporating time stamp
    # make backup folder directory on filesystem
    # create list of items to backup
    # iterate over list of items to backup copying one folder at a time
    # get top level folder name of source and create destination path of backup folder + source folder name
    # do the copy, print out success or error
    # TODO: verify count of files and dirs in backup folder match what was expected to be backed up
    # TODO: check how many previous backup folders exist - complain if more than 3 found
    str_timestamp = ""                  # string formatted timestamp to create unique backups
    str_name_backup_folder = ""         # backup folder name with timestamp   
    str_path_backup_directory = ""      # full os path to backup folder 
    str_source_dir_name = ""            # top level folder name of source to be copied
    str_data_dir = ""                   # loop var containing item from list of important directories
    str_full_path_destination = ""      # built path to backup folder destination including source folder name

    str_timestamp = datetime.now().strftime("%m-%d-%Y-%H%M%S") 
    print("Making safe copy of config files before modification in dir:", graylog_global_vars.str_pth_cwd, "with timestamp:",str_timestamp)
    str_name_backup_folder = "backup-" + str_timestamp
    str_path_backup_directory = graylog_global_vars.str_pth_cwd + str_name_backup_folder
    try:
        if(graylog_global_vars.bool_verbose): print("  Creating backup directory:",str_path_backup_directory)
        os.makedirs(str_path_backup_directory, exist_ok=False)
        # copy each dir from list to backup folder
        for str_data_dir in graylog_global_vars.list_config_directories:
            str_source_dir_name = os.path.basename(str_data_dir)
            str_full_path_destination = os.path.join(str_path_backup_directory, str_source_dir_name)
            shutil.copytree(str_data_dir, str_full_path_destination)
            if(graylog_global_vars.bool_verbose): print(f"    Directory '{str_data_dir}' copied to '{str_full_path_destination}' successfully.")
    except FileExistsError as e:
        print(f"Directory '{e}' already exists.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
    except os.error as e:
        print(f"[Error] An OSError occurred verifying config directories or files: {e}")
        sys.exit(1)
    print("[Done] Making a safe copy of config files.\n")

    