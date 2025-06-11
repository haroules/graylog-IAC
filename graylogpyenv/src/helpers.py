"""src.helpers module"""
import sys
import base64
import os
import json
from typing import Union
import requests
from validators import url
from jqpy import jq

import global_vars

def exit_with_message(message: str, error_code: int) -> None:
    """src.helpers.exit_with_message function"""
    # pass message exit with integer code to cut down on print followed by sys.exit
    print(message)
    sys.exit(error_code)

def is_json_valid(file_path: str) -> bool:
    """src.helpers.is_json_valid function"""
    # check if file exist and can load as json or throws error (return True/False)
    try:
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding="utf-8") as f:
                data=json.load(f)
            if isinstance(data,dict):
                return True
    except json.JSONDecodeError:
        #exit_with_message(f"[ERROR] Problem decoding json in is_json_valid: {file_path}",1)
        return False
    return False

def contains_sublist(sub_list: list, main_list: list) -> bool:
    """src.helpers.contains_sublist function"""
    # simple check if second list contains first list as an item itself
    # return true if it does, false if not
    if not isinstance(sub_list,list) or not isinstance(main_list,list):
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

def remove_sublists(main_list :list, sublist_to_remove :list) -> list:
    """src.helpers.remove_sublists function"""
    int_main_list_count = len(main_list)
    int_sublist_count = len(sublist_to_remove)
    if not int_main_list_count > int_sublist_count:
        print("[ERROR] in remove sublists, main list doesn't have elements to remove")
        sys.exit(1)
    for idstring in sublist_to_remove:
        if idstring in main_list:
            main_list.remove(idstring)
    cleaned_list_count = len(main_list)
    if not cleaned_list_count == ( int_main_list_count - int_sublist_count ):
        print("[ERROR] in remove sublists, new list doesn't have required number of changes")
        sys.exit(1)
    else:
        return main_list

def check_graylog_baseurl(args: list) -> Union[str, bool]:
    """src.helpers.check_graylog_baseurl function"""
    print("Verify graylog baseurl.")

    match = url(args[2])  # check url has valid form
    if not bool(match):
        return f"[ERROR] URL appears malformed: {args[2]}"
    try:
        response = requests.get(args[2],timeout=5)  # check base url responds with no auth
        if response.status_code == 200:
            try:
                responsetext=json.loads(response.text) # check output has a specific expexted response
                if not ("cluster_id" and "node_id" and "version" and "tagline" in responsetext):
                    return f"[ERROR] {args[2]} Didn't provide expected response. Recieved:\n {response.text}"
            except json.JSONDecodeError as e:
                return f"[ERROR] There was a problem decoding json response: {e}, URL: {args[2]}"
    except requests.exceptions.RequestException as e:
        return f"[ERROR] {args[2]} Didn't respond.\n Error was: {e}"
    print("[Done] Verify graylog baseurl.\n")
    return True

def check_api_token(args: list) -> Union[str, bool]:
    """src.helpers.check_api_token function"""
    # perform quick check that token is valid by getting cluster status
    # immediately exit if not status 200, otherwise print status of cluster
    print("Verify api token authenticates and cluster is up.")
    try:
        response = requests.get(args[0],headers=args[1],timeout=5)
        if response.status_code != 200:
            return f"[ERROR] Testing api token failed. Response code:{response.status_code}"
        str_lifecycle_status = jq('.[].lifecycle',json.loads(response.text),raw_output=True).text.strip('"')
        if str_lifecycle_status == "running":
            print("[Done] Token authenticated to cluster and cluster is up.\n")
            return True
        return f"[ERROR] cluster status is not ok. Status:{str_lifecycle_status}"
    except requests.exceptions.RequestException as e:
        return f"[ERROR]  Request error: {e}"
    except json.JSONDecodeError as e:
        return f"There was a problem decoding json: {e}"

def set_global_vars(args: list) -> None:
    """src.helpers.set_global_vars function"""
    # see global_vars for description of each var
    print("Assigning global variables.")
    str_pth_cwd = ""
    # based on positional arguments we have to set cur working directory and verbose flag appropriately
    if len(args)==4:
        global_vars.BOOL_VERBOSE = True # default to verbose if no argument supplied otherwise
        str_pth_cwd = args[3]
    elif len(args)==5:
        global_vars.BOOL_VERBOSE = args[3]
        str_pth_cwd = args[4]

    # built in indexes and streams
    global_vars.LIST_BUILTIN_INDEX_NAMES = ["Default index set","Graylog Events","Graylog System Events"]
    global_vars.LIST_BUILTIN_STREAMS_IDS = ["000000000000000000000001","000000000000000000000002","000000000000000000000003"]

    # set static values for urls
    global_vars.STR_INPUTS_URL = args[2] + "/system/inputs"
    global_vars.STR_INDEXSETS_URL = args[2] + "/system/indices/index_sets"
    global_vars.STR_NODE_ID_URL = args[2] + "/system/cluster/node"
    global_vars.STR_STREAMS_URL = args[2] + "/streams"
    global_vars.STR_CLUSTER_URL = args[2] + "/cluster"
    # set static values for directories
    global_vars.STR_PTH_HOST_CFG_DIR = str_pth_cwd + "/host-configs"
    global_vars.STR_PTH_HOST_CFG_TEMPLATE = str_pth_cwd + "/host-config-templates"
    global_vars.STR_PTH_EXTRCTR_CFG = str_pth_cwd + "/extractors"
    global_vars.STR_PTH_INDICES_CFG = str_pth_cwd + "/indices"
    global_vars.STR_PTH_INPUTS_CFG = str_pth_cwd + "/inputs"
    global_vars.STR_PTH_STREAMS_CFG = str_pth_cwd + "/streams"
    global_vars.STR_PTH_SCHEMAS = str_pth_cwd + "/schemas"
    # set static values for filenames
    global_vars.STR_PTH_HOST_SCHEMA = global_vars.STR_PTH_SCHEMAS + "/schema_host.json"
    global_vars.STR_PTH_SCHEMA_INDEX = global_vars.STR_PTH_SCHEMAS + "/schema_index.json"
    global_vars.STR_PTH_SCHEMA_INPUT = global_vars.STR_PTH_SCHEMAS + "/schema_input.json"
    global_vars.STR_PTH_SCHEMA_EXTRACTOR = global_vars.STR_PTH_SCHEMAS + "/schema_extractor.json"
    global_vars.STR_PTH_SCHEMA_STREAM = global_vars.STR_PTH_SCHEMAS + "/schema_stream.json"
    # list of paths to all important data directories used in:
    global_vars.LIST_CONFIG_DIRECTORIES = [
        global_vars.STR_PTH_HOST_CFG_DIR, global_vars.STR_PTH_HOST_CFG_TEMPLATE,
        global_vars.STR_PTH_EXTRCTR_CFG, global_vars.STR_PTH_INDICES_CFG,
        global_vars.STR_PTH_INPUTS_CFG, global_vars.STR_PTH_STREAMS_CFG,
        global_vars.STR_PTH_SCHEMAS
    ]
    # set tokens and headers dictionaries
    credentials = f"{args[1]}:token"  # Use input token as username and string 'token' as password
    encoded_token = base64.b64encode(credentials.encode()).decode()  # Base64 encode token as required to pass it
    global_vars.DICT_GET_HEADERS = {
        "Authorization": f"Basic {encoded_token}",
        "Content-Type": "application/json",
    }
    global_vars.DICT_POST_HEADERS = {
        "Authorization": f"Basic {encoded_token}",
        "Content-Type": "application/json",
        "X-Requested-By": "XMLHttpRequest",
    }
    print("[Done] Assigning global variables.\n")

def set_global_vars_verify(args: list) -> None:
    """src.helpers.set_global_vars_verify function"""
    print("Assigning global variables.")
    str_path_cwd = ""
    # based on positional arguments we have to set cur working directory and verbose flag appropriately
    if len(args)==2:
        global_vars.BOOL_VERBOSE = True # default to verbose if no argument supplied otherwise
        str_path_cwd = args[1]
    elif len(args)==3:
        global_vars.BOOL_VERBOSE = args[1]
        str_path_cwd = args[2]
    # set static values for directories
    global_vars.STR_PTH_HOST_CFG_DIR = str_path_cwd + "/host-configs"
    global_vars.STR_PTH_HOST_CFG_TEMPLATE = str_path_cwd + "/host-config-templates"
    global_vars.STR_PTH_EXTRCTR_CFG = str_path_cwd + "/extractors"
    global_vars.STR_PTH_INDICES_CFG = str_path_cwd + "/indices"
    global_vars.STR_PTH_INPUTS_CFG = str_path_cwd + "/inputs"
    global_vars.STR_PTH_STREAMS_CFG = str_path_cwd + "/streams"
    global_vars.STR_PTH_SCHEMAS = str_path_cwd + "/schemas"
    # set static values for filenames
    global_vars.STR_PTH_HOST_SCHEMA = global_vars.STR_PTH_SCHEMAS + "/schema_host.json"
    global_vars.STR_PTH_SCHEMA_INDEX = global_vars.STR_PTH_SCHEMAS + "/schema_index.json"
    global_vars.STR_PTH_SCHEMA_INPUT = global_vars.STR_PTH_SCHEMAS + "/schema_input.json"
    global_vars.STR_PTH_SCHEMA_EXTRACTOR = global_vars.STR_PTH_SCHEMAS + "/schema_extractor.json"
    global_vars.STR_PTH_SCHEMA_STREAM = global_vars.STR_PTH_SCHEMAS + "/schema_stream.json"
    # list of paths to all important data directories used in:
    # graylog_verify::verify_configfiles_filesystem
    # graylog_helpers::make_config_backup
    global_vars.LIST_CONFIG_DIRECTORIES = [
        global_vars.STR_PTH_HOST_CFG_DIR, global_vars.STR_PTH_HOST_CFG_TEMPLATE,
        global_vars.STR_PTH_EXTRCTR_CFG, global_vars.STR_PTH_INDICES_CFG,
        global_vars.STR_PTH_INPUTS_CFG, global_vars.STR_PTH_STREAMS_CFG,
        global_vars.STR_PTH_SCHEMAS
    ]
    print("[Done] Assigning global variables.\n")

def check_args(args :list) -> Union[str, list[str,str,str,str], list[str,str,str,bool,str]]:
    """src.helpers.check_args function"""
   # validate inputs to this script
    # input to function is the arguments passed to the script at runtime
    # return args with current working directory appended or
    # return args with verbose flag set as bool and with current working directory appended
    print("Checking arguments and validating the inputs.")
    try:
        if len(args) < 3 or len(args) > 4:   # check 2 or 3 args passed, argv has script name as arg so total should be 3 or 4
            return f"[ERROR] Wrong number of script arguments. Number of args passed:{len(args) - 1}"
        if len(args[1]) != 51:  # check token is 51 characters
            return f"[ERROR] Token was wrong length. Length was:{len(args[1])}"
        if not args[1].isalnum():  # check token is alpha numeric characters only
            return "[ERROR] Token had non alphanumeric characters."
        # check optional Verbose flag set to true or false [case insensitive]
        if len(args) == 4:          # is there a third argument
             # must be string of 4 or 5 chars (true or false)
            if( isinstance(args[3],str) and len(args[3]) > 3 and len(args[3]) < 6):
                str_arg_three = args[3].lower() # put string to all lower case to ease match
                match str_arg_three:
                    case "true":
                        args[3]=True
                    case "false":
                        args[3]=False
                    case _:
                        return "[ERROR] Optional 3rd argument must be string: true or false."
            else:
                return "[ERROR] Optional 3rd argument must be string: true or false."
        # get current directory, and then get parent folder of that for cwd, then append path to args
        args.append(os.path.dirname(os.getcwd()))
    except os.error as e:
        exit_with_message(f"[ERROR] An OSError occurred getting current working directory: {e}",1)
    print("[Done] Checking arguments and validating the inputs.\n")
    return args

def check_args_verify(args :list) -> Union[str, list[str,str], list[str,bool,str]]:
    """src.helpers.check_args_verify function"""
   # validate inputs to this script
    # input to function is the arguments passed to the script at runtime
    # return args with current working directory appended or
    # return args with verbose flag set as bool and with current working directory appended
    print("Checking arguments and validating the inputs.")
    try:
        if len(args) > 2:   # check 1  or 2 args passed, argv has script name as arg 0 so total should be 1 or 2
            return f"[ERROR] Wrong number of script arguments. Number of args passed:{len(args) - 1}"
        # check optional Verbose flag set to true or false [case insensitive]
        if len(args) == 2:
            # must be string of 4 or 5 chars (true or false)
            if isinstance(args[1],str) and len(args[1]) > 3 and len(args[1]) < 6:
                str_arg_one = args[1].lower() # put string to all lower case to ease match
                match str_arg_one:
                    case "true":
                        args[1]=True
                    case "false":
                        args[1]=False
                    case _:
                        return "[ERROR] Optional argument must be string: true or false."
            else:
                return "[ERROR] Optional argument must be string: true or false."
        # get current directory, and then get parent folder of that for cwd, then append path to args
        args.append(os.path.dirname(os.getcwd()))
    except os.error as e:
        exit_with_message(f"[ERROR] An OSError occurred getting current working directory: {e}",1)
    print("[Done] Checking arguments and validating the inputs.\n")
    return args

def do_init(args) -> list:
    """src.helpers.do_init function"""
    validargs = check_args(args)
    if isinstance(validargs,str):
        print(validargs)
        usage(args)
        sys.exit(1)
    set_global_vars(validargs)
    baseurlok=check_graylog_baseurl(validargs)
    if isinstance(baseurlok,str):
        print(baseurlok)
        sys.exit(1)
    tokenok=check_api_token([global_vars.STR_CLUSTER_URL,global_vars.DICT_GET_HEADERS])
    if isinstance(tokenok,str):
        print(tokenok)
        sys.exit(1)
    return validargs

def usage(valid_args) -> None:
    """src.helpers.usage function"""
    common_message = (
        "  -Admin token and url are required, verbose defaults to True if not set (to False).\n"
        "  -Token should be 52 alpha-numeric characters.\n"
        "  -URL should be of the form http(s)://host|ip:port.\n"
        "  -Setting verbose to False will supress output.\n"
    )
    if valid_args[0] == "graylog_setup.py":
        print("Usage: graylog_setup.py <admin token> <url> <verbose>")
        print(common_message)
    elif valid_args[0] == "graylog_clean.py":
        print("CAREFUL! Running this will delete all data on your graylog instance.")
        print("Usage: graylog_clean.py <admin token> <url> <verbose>")
        print(common_message)
    elif valid_args[0] == "graylog_verify.py":
        print("Usage: graylog_verify.py <verbose>")
        print("  -Verbose defaults to True if not set (to False).")
        print("  -Setting verbose to False will supress output.\n")
