"""Module:src.setup"""
import os
import json
from typing import Union
import requests
from jqpy import jq

from src.helpers import exit_with_message
from src.helpers import contains_sublist
import global_vars

def get_list_config_files(bool_verbose :bool, str_pth_cfg :str, object_type :str) -> list:
    """Function:get_list_config_files"""
    str_config_file = ""
    str_config_file_path = ""
    list_config_files = []
    int_config_file_count = 0
    try:
        for str_config_file in os.listdir(str_pth_cfg):
            str_config_file_path = os.path.join(str_pth_cfg, str_config_file)
            list_config_files.append(str_config_file_path)
            int_config_file_count += 1
        if int_config_file_count == 0:
            exit_with_message(f"[ERROR] No config files found for creating {object_type}. Exiting.",1)
        if bool_verbose:
            print(f"  {int_config_file_count} {object_type} config files to process.")
    except os.error as e:
        exit_with_message(f"[ERROR] An OSError occurred getting list of {object_type} config files. Error was: {e}",1)
    return list_config_files

def create_indices(bool_verbose :bool,str_pth_indices_cfg :str,
    str_indexsets_url :str, dict_post_headers :dict) -> None:
    """Function:create_indices"""
    str_index_id = ""
    str_index_name = ""
    str_index_input_file = ""
    int_index_processed_count = 0
    dict_index_config = {}
    list_index_input_files = []

    print("Processing indexes")
    try:
        list_index_input_files = get_list_config_files(bool_verbose,str_pth_indices_cfg, "index")
        for str_index_input_file in list_index_input_files:
            if bool_verbose:
                print(f"    Creating index from config: {str_index_input_file}")
            with open(str_index_input_file, "r", encoding="utf-8") as file:
                dict_index_config = json.load(file)
                index_post_response = requests.post(str_indexsets_url, headers=dict_post_headers,
                    json=dict_index_config,timeout=3)
                match index_post_response.status_code:
                    case 400:
                        if bool_verbose:
                            print(f"      Index already exists:{index_post_response.text}")
                        int_index_processed_count += 1
                    case 200:
                        str_index_id = jq('.id',json.loads(index_post_response.text))
                        str_index_name = jq('.title',json.loads(index_post_response.text))
                        if bool_verbose:
                            print(f"      Index:{str_index_name} Id:{str_index_id} was created")
                        int_index_processed_count += 1
                    case _:
                        exit_with_message(f"[ERROR] Create index {str_index_input_file} Message: {index_post_response.text}",1)
    except FileNotFoundError as e:
        exit_with_message(f"[ERROR]: File or directory not found. Couln't open index config file {e}",1)
    except json.JSONDecodeError as e:
        exit_with_message(f"[ERROR] There was a problem decoding json in create indices: {e}",1)
    except requests.exceptions.RequestException as e:
        exit_with_message(f"[ERROR] Request error in create indices: {e}",1)
    print("[Done] processing indexes.\n")

def update_nodeid_in_input_config_files(bool_verbose :bool, list_input_config_files: list,
    str_node_id_url: str, dict_get_headers: dict) -> None:
    """Function:update_nodeid_in_input_config_files"""

    node_id_response = ""
    node_id = []
    str_input_file_path = ""
    str_input_file_content = ""
    str_node_id = ""
    input_json_content = ""
    try:
        node_id_response = requests.get(str_node_id_url, headers=dict_get_headers, timeout=3)
        node_id_response.raise_for_status()
        if node_id_response.status_code != 200:
            exit_with_message(f"[ERROR] API call to: {str_node_id_url} Failed. Message: {node_id_response.text}",1)
        json_node_response = json.loads(node_id_response.text)
        node_id = jq('.node_id',json_node_response)
        if bool_verbose:
            print(f"  Replace nodeid: {node_id[0]} in input config files.")
        for str_input_file_path in list_input_config_files:
            if bool_verbose:
                print(f"    Updating node id in:{str_input_file_path}")
            with open(str_input_file_path, "r", encoding="utf-8") as file:
                str_input_file_content = file.read() # load config file content
            input_json_content = json.loads(str_input_file_content) # convert loaded file content to json
            str_node_id = str(node_id[0])  # store nodeid as string var
            if "node" in input_json_content:  # verify specific field exists
                input_json_content["node"] = str_node_id  # replace existing node id with new one
                with open(str_input_file_path, "w", encoding="utf-8") as file:  # write back to file
                    json.dump(input_json_content,file, indent=2)
            else:
                exit_with_message(f"[ERROR] Couldn't update config file {str_input_file_path} with {str_node_id}",1)
    except FileNotFoundError as e:
        exit_with_message(f"[ERROR]: File or directory not found in update_nodeid_in_input_config_files: {e}",1)
    except json.JSONDecodeError as e:
        exit_with_message(f"[ERROR] There was a problem decoding json in update_nodeid_in_input_config_files: {e}",1)
    except requests.exceptions.RequestException as e:
        exit_with_message(f"[ERROR] Request error in update_nodeid_in_input_config_files: {e}",1)

def gen_list_inputs_titles(str_inputs_url: str, dict_get_headers: dict) -> list:
    """Function:gen_list_inputs_titles"""
    try:
        inputs_get_response = ""    #api response object to get list of inputs
        titlesfound = []
        inputs_get_response = requests.get(str_inputs_url, headers=dict_get_headers,timeout=3)
        inputs_get_response.raise_for_status()
        if inputs_get_response.status_code != 200:
            exit_with_message(f"[ERROR] API call to: {str_inputs_url} Failed. Message: {inputs_get_response.text}",1)
        inputs_response_json = json.loads(inputs_get_response.text)
        titlesfound = jq('.inputs[].title',data=inputs_response_json)
    except json.JSONDecodeError as e:
        exit_with_message(f"[ERROR] There was a problem decoding json in gen_list_inputs_titles: {e}",1)
    except requests.exceptions.RequestException as e:
        exit_with_message(f"[ERROR] Request error in gen_list_inputs_titles: {e}",1)
    return titlesfound

def gen_list_inputs_to_create(bool_verbose :bool, list_input_config_files: list,
    str_inputs_url: str, dict_get_headers: dict) -> list:
    """Function:gen_list_inputs_to_create"""

    str_input_file_path = ""
    input_json_content = ""
    input_name_json = []
    input_titles_found = []
    list_inputs_to_create = []
    try:
        input_titles_found = gen_list_inputs_titles(str_inputs_url, dict_get_headers)
        for str_input_file_path in list_input_config_files:
            with open(str_input_file_path, "r", encoding="utf-8") as file:
                str_input_file_content = file.read()
            input_json_content = json.loads(str_input_file_content) # convert loaded file content to json
            input_name_json = jq('.title',input_json_content)
            if contains_sublist(input_name_json,input_titles_found):
                if bool_verbose:
                    print(f"    {input_name_json[0]} Input already exists, skipping creation")
            else:
                list_inputs_to_create.append(str_input_file_path)
    except FileNotFoundError as e:
        exit_with_message(f"[ERROR]: File or directory not found in gen_list_inputs_to_create: {e}",1)
    except json.JSONDecodeError as e:
        exit_with_message(f"[ERROR] There was a problem decoding json in gen_list_inputs_to_create: {e}",1)
    return list_inputs_to_create

def create_inputs(bool_verbose :bool, str_pth_inputs_cfg :str, str_node_id_url :str,
    str_inputs_url :str, dict_get_headers :dict, dict_post_headers :dict) -> None:
    """Function:create_inputs"""

    list_input_config_files = []
    list_inputs_to_create = []
    str_input_file_path = ""
    str_input_file_content = ""
    input_json_content = ""
    inputs_post_response = ""
    json_created_input_id = []
    print("Processing inputs")
    try:
        list_input_config_files=get_list_config_files(bool_verbose, str_pth_inputs_cfg, "input")
        update_nodeid_in_input_config_files(bool_verbose, list_input_config_files,str_node_id_url,dict_get_headers)
        list_inputs_to_create = gen_list_inputs_to_create(bool_verbose, list_input_config_files,str_inputs_url,dict_get_headers)
        for str_input_file_path in list_inputs_to_create:
            with open(str_input_file_path, "r", encoding="utf-8") as file:
                str_input_file_content = file.read()
            input_json_content = json.loads(str_input_file_content)
            input_name_json = jq('.title',input_json_content)
            inputs_post_response = requests.post(str_inputs_url, headers=dict_post_headers, json=input_json_content, timeout=3)
            inputs_post_response.raise_for_status()
            match inputs_post_response.status_code:
                case 201:
                    response_json = json.loads(inputs_post_response.text)
                    json_created_input_id = response_json["id"]
                    if bool_verbose:
                        print(f"    InputTitle: {input_name_json[0]} InputID: {json_created_input_id} Created.")
                case _:
                    exit_with_message(f"[ERROR] Create input failed. Message: {inputs_post_response.text}",1)
        print("[Done] Processing inputs.\n")
    except FileNotFoundError as e:
        exit_with_message(f"[ERROR]: File or directory not found in create inputs: {e}",1)
    except json.JSONDecodeError as e:
        exit_with_message(f"[ERROR] There was a problem decoding json in create inputs: {e}",1)
    except requests.exceptions.RequestException as e:
        exit_with_message(f"[ERROR] Request error in create inputs: {e}",1)

def create_static_fields(bool_verbose :bool, str_inputs_url :str, dict_get_headers :dict, dict_post_headers :dict) -> None:
    """Function:create_static_fields"""
    json_titles_found = ""
    str_static_field_url = ""
    json_static_payload = ""
    json_inputs_count = ""

    print("Processing static fields")
    try:
        inputs_get_response = requests.get(str_inputs_url, headers=dict_get_headers, timeout=3)
        inputs_get_response.raise_for_status()
        if inputs_get_response.status_code != 200:
            exit_with_message(f"[ERROR] API call to: {str_inputs_url} Failed. Message: {inputs_get_response.text}",1)
        inputs_get_data = json.loads(inputs_get_response.text)
        json_titles_found = jq('.inputs[] | [ .title,.id ]',data=inputs_get_data)
        json_inputs_count = len(json_titles_found)
        if json_inputs_count == 0:
            exit_with_message("[ERROR] No inputs found. Exiting",1)
        if bool_verbose:
            print(f"  {json_inputs_count} Static fields to process.")
        for static_field_keypair in json_titles_found:
            str_static_field_url = str_inputs_url + "/" + static_field_keypair[1] + "/staticfields"
            json_static_payload = '{"key":"input","value":"' + static_field_keypair[0] + '"}'
            create_static_field_response = requests.post(str_static_field_url, headers=dict_post_headers,
                json=json.loads(json_static_payload),timeout=3)
            create_static_field_response.raise_for_status()
            if create_static_field_response.status_code != 201:
                exit_with_message(f"[ERROR] Add static field failed. Message:{create_static_field_response.text}",1)
            else:
                if bool_verbose:
                    print(f"  Static field added: {json_static_payload}")
        print("[Done] Processing static fields.\n")
    except json.JSONDecodeError as e:
        exit_with_message(f"[ERROR] There was a problem decoding json in create_static_fields: {e}",1)
    except requests.exceptions.RequestException as e:
        exit_with_message(f"[ERROR] Request error in create_static_fields: {e}",1)

def gen_list_host_config_sets(bool_verbose :bool, str_pth_host_cfg_dir :str, str_path_host_config_file :str) -> list:
    """Function:gen_list_host_config_sets"""
    int_total_xtrctrs_in_configfile = 0
    str_full_pth_host_cfg_file = ""
    dict_host_config = []
    list_xtrctr_counts_in_configfile = []
    xtrctr_count_in_config_set = ""
    try:
        str_full_pth_host_cfg_file = os.path.join(str_pth_host_cfg_dir,str_path_host_config_file)
        with open(str_full_pth_host_cfg_file, "r", encoding="utf-8") as hostconfigfile:
            dict_host_config=json.load(hostconfigfile)
        # each config file may have multiple config sets so have to create a list of config counts
        list_xtrctr_counts_in_configfile=jq('.config_sets[].extractors_total',dict_host_config)
        for xtrctr_count_in_config_set in list_xtrctr_counts_in_configfile:
            int_total_xtrctrs_in_configfile += int(xtrctr_count_in_config_set)
        if bool_verbose:
            print(f"  {str_full_pth_host_cfg_file} has {int_total_xtrctrs_in_configfile} extractors defined")
    except FileNotFoundError as e:
        exit_with_message(f"[ERROR]: File or directory not found in gen_list_host_config_sets: {e}",1)
    except json.JSONDecodeError as e:
        exit_with_message(f"[ERROR] There was a problem decoding json in gen_list_host_config_sets: {e}",1)
    return jq('.config_sets[]',dict_host_config)

def gen_list_extractor_details(host_config_set: list, str_inputs_url :str, dict_get_headers :dict) -> list:
    """Function:gen_list_extractor_details"""
    int_tot_xtrctrs_in_configset = 0
    str_input_title =[]
    list_extractor_config_files = []
    get_inputs_response = ""
    str_jqfilter = ""
    str_inputid = ""
    try:
        # its possible that an extractor isn't configured for a config set, so get count for config set
        list_extractors_total = jq('.extractors_total',host_config_set)
        int_tot_xtrctrs_in_configset = int(list_extractors_total[0])
        # if 0 extractors are found skip config set otherwise create or skip if already exists
        if int_tot_xtrctrs_in_configset > 0:
            str_input_title=jq('.input_title',host_config_set,raw_output=True).text
            list_extractor_config_files=jq('.extractors[].extractor_config_file',host_config_set)
            # get list of all inputs
            get_inputs_response = requests.get(str_inputs_url, headers=dict_get_headers, timeout=3)
            get_inputs_response.raise_for_status()
            if get_inputs_response.status_code != 200:
                exit_with_message(f"[ERROR] API call to: {str_inputs_url} Failed. Message: {get_inputs_response.text}",1)
            # build jq filter string to get id of input with title from variable
            str_jqfilter = '.inputs[] | select(.title == ' + str_input_title + ') | .id'
            # jq query to get input id from all inputs receieved from API
            inputs_json = json.loads(get_inputs_response.text)
            str_inputid = jq(str_jqfilter,data=inputs_json)
            #str_inputid = jq(str_jqfilter,data=inputs_json,raw_output=True).text.strip('"')
    except requests.exceptions.RequestException as e:
        exit_with_message(f"[ERROR] Request error in gen_list_extractor_details: {e}",1)
    return [str_inputid[0], str_input_title, list_extractor_config_files]

def check_extractor_exists(bool_verbose :bool, extractor_id :str,
        extractor_file :str, str_inputs_url :str, dict_get_headers : dict) -> Union [ bool, str ]:
    """Function:check_extractor_exists"""
    str_get_xtractr_by_id_url = ""
    get_xtractr_response = ""
    str_xtrctr_title = []
    list_existing_xtrctr = []
    try:
        # build url to query extractors of an input from its id
        str_get_xtractr_by_id_url = str_inputs_url + "/" + extractor_id + "/extractors"
        get_xtractr_response = requests.get(str_get_xtractr_by_id_url, headers=dict_get_headers, timeout=3)
        get_xtractr_response.raise_for_status()
        #if get_xtractr_response.status_code != 200 and get_xtractr_response.status_code != 404:
            #exit_with_message(f"[ERROR] API call to: {str_get_xtractr_by_id_url} Failed. Message: {get_xtractr_response.text}",1)
        # check if the response from input by id already has extractors defined in a list
        with open(os.path.join(global_vars.STR_PTH_EXTRCTR_CFG,extractor_file), "r", encoding="utf-8") as file:
            str_xtrctr_title=jq('.title',data=json.load(file))
        list_existing_xtrctr=jq('.extractors[].title',json.loads(get_xtractr_response.text))
        # make sure extractors title isn't in the list we just got , add if they don't
        if contains_sublist(str_xtrctr_title,list_existing_xtrctr):
            if bool_verbose:
                print(f"     Extractor {str_xtrctr_title} already exists")
            return True
    except FileNotFoundError as e:
        exit_with_message(f"[ERROR] File or directory not found in check_extractor_exists: {e}",1)
    except requests.exceptions.RequestException as e:
        exit_with_message(f"[ERROR] Request error in check_extractor_exists: {e}",1)
    return str_xtrctr_title

def create_extractors(bool_verbose :bool, str_pth_extrctr_cfg :str, str_pth_host_cfg_dir :str, str_inputs_url :str,
        dict_get_headers :dict, dict_post_headers :dict) -> None:
    """Function:create_extractors"""
    print("Processing extractors")
    try:
        if bool_verbose:
            print(f"  {len(os.listdir(str_pth_extrctr_cfg))} Extractor config files to process.")
        for str_path_host_config_file in os.listdir(str_pth_host_cfg_dir): # loop on list of host config files found in directory
            list_config_sets=gen_list_host_config_sets(bool_verbose,str_pth_host_cfg_dir,str_path_host_config_file)
            for config_set in list_config_sets:
                # its possible that an extractor isn't configured for a config set, so get count for config set
                if int(jq('.extractors_total',config_set,raw_output=True).text) > 0:
                    list_extractor_details = gen_list_extractor_details(config_set,str_inputs_url,dict_get_headers)
                    for xtrctr_file in list_extractor_details[2]:
                        returnval=check_extractor_exists(bool_verbose,list_extractor_details[0],
                            xtrctr_file, str_inputs_url, dict_get_headers)
                        if isinstance(returnval,list):
                            if bool_verbose:
                                print(f"     Creating extractor: {returnval} for input {list_extractor_details[1]}")
                            with open(os.path.join(str_pth_extrctr_cfg,xtrctr_file), "r", encoding="utf-8") as xtrctr_config_file:
                                str_get_xtractr_by_id_url = str_inputs_url + "/" + list_extractor_details[0] + "/extractors"
                                xtrctr_add_response = requests.post(str_get_xtractr_by_id_url, headers=dict_post_headers,
                                    json=json.load(xtrctr_config_file),timeout=3)
                                # check if we were succesful in adding extractor to input this seems goofy should success be 200
                                if xtrctr_add_response.status_code != 201:
                                    exit_with_message(f"[ERROR] Add extractor failed. Message:{xtrctr_add_response.text}",1)
                                else:
                                    if bool_verbose:
                                        print(f"    Extractor added: {xtrctr_add_response.text}")
        print("[Done] processing extractors.\n")
    except FileNotFoundError as e:
        exit_with_message(f"[ERROR] File or directory not found in create_extractors: {e}",1)
    except requests.exceptions.RequestException as e:
        exit_with_message(f"[ERROR] Request error in create_extractors: {e}",1)
    except json.JSONDecodeError as e:
        exit_with_message(f"[ERROR] There was a problem decoding json in create_extractors: {e}",1)

def gen_list_host_config_files(bool_verbose :bool, str_pth_host_cfg_dir :str) -> list:
    """Function:gen_list_host_config_files"""
    list_host_config_files = []
    try:
        for str_path_host_config_file in os.listdir(str_pth_host_cfg_dir):
            str_full_pth_host_cfg_file = os.path.join(str_pth_host_cfg_dir,str_path_host_config_file)
            if bool_verbose:
                print(f"  Adding host config to list:{str_full_pth_host_cfg_file}")
            list_host_config_files.append(str_full_pth_host_cfg_file)
    except os.error as e:
        exit_with_message(f"[ERROR] An OSError occurred in gen_list_host_config_files: {e}",1)
    return list_host_config_files

def update_index_id_in_stream_config_file(bool_verbose :bool, host_config_file :str, str_pth_streams_cfg :str,
        str_indexsets_url :str, dict_get_headers :dict) -> None:
    """Function:update_index_id_in_stream_config_file"""
    try:
        with open(host_config_file, "r", encoding="utf-8") as hostconfigfile:
            dict_host_config=json.load(hostconfigfile)
        list_config_sets=jq('.config_sets[]',dict_host_config)
        for config_set in list_config_sets:
            stream_config_file = config_set["stream_config_file"]
            index_title = config_set["index_title"]
            str_pth_stream_config_file = os.path.join(str_pth_streams_cfg,stream_config_file)
            # get indexsetid from api to replace in config files
            str_searchindexsetbyname_url=str_indexsets_url + "/search?searchTitle=" + index_title
            indexset_id_response = requests.get(str_searchindexsetbyname_url, headers=dict_get_headers,timeout=3)
            if indexset_id_response.status_code != 200:
                exit_with_message(f"[ERROR] Get index id by index name failed. Message:{indexset_id_response.text}",1)
            indexset_json = json.loads(indexset_id_response.text)
            #json_indexset_id = jq('.index_sets[].id',indexset_json,raw_output=True).text.strip('"')
            json_indexset_id = jq('.index_sets[].id',indexset_json)
            # replace indexsetid in config file
            with open(str_pth_stream_config_file, "r", encoding="utf-8") as streamconfigfile:
                dict_stream_config=json.load(streamconfigfile)
            if "index_set_id" in dict_stream_config:
                if bool_verbose:
                    print(f"    Updating {stream_config_file} with index id {json_indexset_id[0]}")
                dict_stream_config["index_set_id"] = json_indexset_id[0]
                with open(str_pth_stream_config_file, "w", encoding="utf-8") as file:
                    json.dump(dict_stream_config, file, indent=2)
            else:
                exit_with_message(f"[ERROR] Couldn't update stream config file {str_pth_stream_config_file}",1)
    except FileNotFoundError as e:
        exit_with_message(f"[ERROR] File or directory not found in update_index_id_in_stream_config_file: {e}",1)
    except requests.exceptions.RequestException as e:
        exit_with_message(f"[ERROR] Request error in update_index_id_in_stream_config_file: {e}",1)
    except json.JSONDecodeError as e:
        exit_with_message(f"[ERROR] There was a problem decoding json in update_index_id_in_stream_config_file: {e}",1)

def gen_list_streams_to_create(bool_verbose :bool, list_host_config_files :list, str_streams_url :str,dict_get_headers) -> list:
    """Function:gen_list_streams_to_create"""
    list_streams_to_create = []
    try:
        for host_config_file in list_host_config_files:
            with open(host_config_file, "r", encoding="utf-8") as hostconfigfile:
                dict_host_config=json.load(hostconfigfile)
            list_config_sets=jq('.config_sets[]',dict_host_config)
            for config_set in list_config_sets:
                stream_config_file = config_set["stream_config_file"]
                new_stream_title = config_set["stream_title"]
                stream_response=requests.get(str_streams_url, headers=dict_get_headers,timeout=3)
                if stream_response.status_code != 200:
                    exit_with_message(f"[ERROR] Get streams failed. Message: {stream_response.text}",1)
                existing_stream_titles = jq('.streams[].title',json.loads(stream_response.text))
                if new_stream_title in existing_stream_titles:
                    if bool_verbose:
                        print(f"      Stream {new_stream_title} Already exists, won't create.")
                else:
                    list_streams_to_create.append([new_stream_title, stream_config_file])
    except FileNotFoundError as e:
        exit_with_message(f"[ERROR] File or directory not found in gen_list_streams_to_create: {e}",1)
    except requests.exceptions.RequestException as e:
        exit_with_message(f"[ERROR] Request error in gen_list_streams_to_create: {e}",1)
    except json.JSONDecodeError as e:
        exit_with_message(f"[ERROR] There was a problem decoding json in gen_list_streams_to_create: {e}",1)
    return list_streams_to_create

def start_stream(str_stream_id :str, str_streams_url :str, dict_post_headers :dict) -> None:
    """Function:start_stream"""
    # newly created streams don't autostart, so start stream
    start_stream_url = str_streams_url + "/" + str_stream_id + "/resume"
    start_stream_response=requests.post(start_stream_url,headers=dict_post_headers, timeout=3)
    if start_stream_response.status_code != 204:
        exit_with_message(f"[ERROR] Start streams failed. Message: {start_stream_response.text}",1)

def create_streams(bool_verbose :bool,str_pth_streams_cfg :str, str_pth_host_cfg_dir :str, str_indexsets_url :str,
        str_streams_url :str, dict_get_headers :dict, dict_post_headers :dict) -> None:
    """Function:create_streams"""
    print("Processing streams")
    try:
        int_strm_cfg_file_count = len(os.listdir(str_pth_streams_cfg))
        if bool_verbose:
            print(f" {int_strm_cfg_file_count} Stream configs to process.")
        list_host_config_files = gen_list_host_config_files(bool_verbose,str_pth_host_cfg_dir)
        for host_config_file in list_host_config_files:
            update_index_id_in_stream_config_file(bool_verbose,host_config_file,str_pth_streams_cfg,
                str_indexsets_url,dict_get_headers)
        list_stream_configs = gen_list_streams_to_create(bool_verbose,list_host_config_files,str_streams_url,dict_get_headers)
        for stream_to_create in list_stream_configs:
            if bool_verbose:
                print(f"      Create Stream {stream_to_create[0]} from config {stream_to_create[1]}")
            stream_config_path = os.path.join(str_pth_streams_cfg,stream_to_create[1])
            with open(stream_config_path, "r", encoding="utf-8") as streamconfigfile:
                dict_stream_config=json.load(streamconfigfile)
            # create stream
            create_stream_response=requests.post(str_streams_url, headers=dict_post_headers,json=dict_stream_config, timeout=3)
            if create_stream_response.status_code != 201:
                exit_with_message(f"[ERROR] Create streams failed. Message: {create_stream_response.text}",1)
            # get newly created stream id from return message
            new_stream_id=jq('.stream_id',json.loads(create_stream_response.text),raw_output=True).text.strip('"')
            start_stream(new_stream_id,str_streams_url,dict_post_headers)
        print("[Done] Processing streams.\n")
    except FileNotFoundError as e:
        exit_with_message(f"[ERROR] File or directory not found in create_streams: {e}",1)
    except requests.exceptions.RequestException as e:
        exit_with_message(f"[ERROR] Request error in create_streams: {e}",1)
    except json.JSONDecodeError as e:
        exit_with_message(f"[ERROR] There was a problem decoding json in create_streams: {e}",1)
