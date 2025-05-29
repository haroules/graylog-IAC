"""src.clean module"""

import json
from typing import Tuple
import requests
from jqpy import jq
from src.helpers import remove_sublists
from src.helpers import exit_with_message

def get_clean_list_ids_to_delete(list_all_ids :list, list_builtin_ids: list) -> list:
    """src.clean.get_clean_list_ids_to_delete function"""
    list_clean_ids = [] # ids list without built ins
    list_clean_ids = remove_sublists(list_all_ids,list_builtin_ids)
    return list_clean_ids

def get_list_all_stream_ids(str_streams_url :str, dict_get_headers: dict) -> list:
    """src.clean.get_list_all_stream_ids function"""
    list_all_streams_ids = []
    try:
        response_streams = requests.get(str_streams_url, headers=dict_get_headers, timeout=3)
        response_streams.raise_for_status()
        if response_streams.status_code == 200:
            list_all_streams_ids = jq('.streams[].id',json.loads(response_streams.text))
    except requests.exceptions.RequestException as e:
        exit_with_message(f"[ERROR] Request error in get_list_all_stream_ids: {e}\n",1)
    except ValueError as e:
        exit_with_message(f"[ERROR] JSON decoding error in get_list_all_stream_ids: {e}\n",1)
    return list_all_streams_ids

def get_list_stream_names_to_delete(list_stream_ids_to_delete :list, str_streams_url :str, dict_get_headers :dict) -> list:
    """src.clean.get_list_stream_names_to_delete function"""
    list_clean_names = [] # names list without built ins
    for stream_id in list_stream_ids_to_delete:
        try:
            str_streamsurlbyid = str_streams_url + "/" + stream_id # get stream by id filter out name
            response_streams_byname = requests.get(str_streamsurlbyid, headers=dict_get_headers, timeout=3)
            response_streams_byname.raise_for_status()
            if response_streams_byname.status_code == 200:
                list_streamname = jq('.title',json.loads(response_streams_byname.text))
                # response returns list of 1, convert to string and append to built in list of ids
                list_clean_names.append("".join(list_streamname))
            else:
                exit_with_message(f"[ERROR] Couldn't find id. {stream_id}\n",1)
        except requests.exceptions.RequestException as e:
            exit_with_message(f"[ERROR] Request error in get_list_stream_names_to_delete: {e}\n",1)
        except ValueError as e:
            exit_with_message(f"[ERROR] JSON decoding error in get_list_stream_names_to_delete: {e}\n",1)
    return list_clean_names

def remove_streams(bool_verbose :bool, str_streams_url :str, dict_get_headers :dict, dict_post_headers :dict,
        list_builtin_streams_ids :list) -> bool:
    """src.clean.remove_streams function"""
    response_delete_stream = ""  # python response object from delete stream api endpoint
    str_deleteurl = "" # delete streams api endpoint
    list_stream_names_to_delete = [] # list of all stream names from streams api endpoint
    list_all_streams_ids = [] # list of all stream ids from streams api endpoint
    list_stream_ids_to_delete = [] # updated list of stream ids with built in ones removed

    print("Processing streams for deletion")
    list_all_streams_ids = get_list_all_stream_ids(str_streams_url, dict_get_headers)
    if len(list_all_streams_ids) < 4:
        if bool_verbose:
            print("No streams to delete.")
        print("[Done] processing streams for deletion.\n")
        return True
    list_stream_ids_to_delete = get_clean_list_ids_to_delete(list_all_streams_ids,list_builtin_streams_ids)
    if isinstance(list_stream_ids_to_delete, list):
        if bool_verbose:
            print(f"{len(list_stream_ids_to_delete)} Streams found")
    list_stream_names_to_delete = get_list_stream_names_to_delete(list_stream_ids_to_delete,str_streams_url,dict_get_headers)
    if bool_verbose:
        print(f"Removing Stream Ids {list_stream_ids_to_delete}")
        print(f"Removing Stream Titles {list_stream_names_to_delete}")
    for stream_id in list_stream_ids_to_delete:
        try:
            str_deleteurl = str_streams_url + "/" + stream_id
            response_delete_stream = requests.delete(str_deleteurl, headers=dict_post_headers,timeout=3)
            response_delete_stream.raise_for_status()
            if not response_delete_stream.status_code == 204:
                exit_with_message(f"[ERROR] Failed to delete stream: {stream_id}\n",1)
        except requests.exceptions.RequestException as e:
            exit_with_message(f"[ERROR] Request error in remove streams: {e}\n",1)
        except ValueError as e:
            exit_with_message(f"[ERROR] JSON decoding error in remove streams: {e}\n",1)
    print("[Done] processing streams for deletion.\n")
    return True

def gen_list_inputs_to_delete(str_inputs_url: str, dict_get_headers: dict) -> Tuple[list, list]:
    """src.clean.gen_list_inputs_to_delete function"""
    list_input_ids = []
    list_input_names = []
    try:
        response_list_inputs = requests.get(str_inputs_url, headers=dict_get_headers, timeout=3)
        response_list_inputs.raise_for_status()
        if response_list_inputs.status_code == 200:
            list_input_ids = jq('.inputs[].id',json.loads(response_list_inputs.text))
            list_input_names = jq('.inputs[].title',json.loads(response_list_inputs.text))
    except requests.exceptions.RequestException as e:
        exit_with_message(f"[ERROR] Request error in gen_list_inputs_to_delete: {e}\n",1)
    except ValueError as e:
        exit_with_message(f"[ERROR] JSON decoding error in gen_list_inputs_to_delete: {e}\n",1)
    return list_input_ids, list_input_names

def remove_inputs(bool_verbose :bool, str_inputs_url :str, dict_get_headers :dict, dict_post_headers :dict) -> bool:
    """src.clean.remove_inputs function"""
    str_delete_input_byid_url = "" # delete inputs api endpoint
    list_input_ids_to_delete = [] # all input ids
    list_input_names_to_delete = [] # all input names

    print("Processing inputs for deletion")
    tuple_fnctn_returnval: Tuple[list,list] = gen_list_inputs_to_delete(str_inputs_url,dict_get_headers)
    list_input_ids_to_delete, list_input_names_to_delete = tuple_fnctn_returnval
    if len(list_input_ids_to_delete) == 0:
        if bool_verbose:
            print("No inputs to delete")
        print("[Done] processing inputs for deletion.\n")
        return True
    if bool_verbose:
        print(f"{len(list_input_ids_to_delete)} Inputs found")
        print(f"Removing Input Ids {list_input_ids_to_delete}")
        print(f"Removing Input Titles {list_input_names_to_delete}")
    for input_id in list_input_ids_to_delete:
        try:
            str_delete_input_byid_url = str_inputs_url + "/" + input_id
            response_delete_input = requests.delete(str_delete_input_byid_url, headers=dict_post_headers,timeout=3)
            response_delete_input.raise_for_status()
            if response_delete_input.status_code != 204:
                exit_with_message(f"[ERROR] Failed to delete input: {input_id}",1)
        except requests.exceptions.RequestException as e:
            exit_with_message(f"Request error in remove_inputs: {e}",1)
        except ValueError as e:
            exit_with_message(f"JSON decoding error in remove_inputs: {e}",1)
    print("[Done] processing inputs for deletion.\n")
    return True

def get_list_all_index_sets_ids(str_indexsets_url :str, dict_get_headers: dict) -> list:
    """src.clean.get_list_all_index_sets_ids function"""
    list_all_index_ids = []
    try:
        response_list_indexsets = requests.get(str_indexsets_url, headers=dict_get_headers, timeout=3)
        response_list_indexsets.raise_for_status()
        if response_list_indexsets.status_code == 200:
            list_all_index_ids = jq('.index_sets[].id',json.loads(response_list_indexsets.text))
        else:
            exit_with_message(f"[ERROR] Couldn't find id. {response_list_indexsets.text}",1)
    except requests.exceptions.RequestException as e:
        exit_with_message(f"[ERROR] Request error in get_list_all_index_sets_ids: {e}",1)
    except ValueError as e:
        exit_with_message(f"[ERROR] JSON decoding error in get_list_all_index_sets_ids: {e}",1)
    return list_all_index_ids

def get_list_all_builtin_index_set_ids(str_indexsets_url :str,dict_get_headers :dict,list_builtin_index_names: list) -> list:
    """src.clean.get_list_all_builtin_index_set_ids function"""
    list_builtin_indexids = []
    try:
        for str_index_name in list_builtin_index_names:
            str_search_url = str_indexsets_url + "/search?searchTitle="
            str_get_index_id_by_name_url = str_search_url + str_index_name + "&skip=0&limit=0&stats=false"
            response_getindexidbyname = requests.get(str_get_index_id_by_name_url,
                headers=dict_get_headers, timeout=3)
            response_getindexidbyname.raise_for_status()
            if response_getindexidbyname.status_code == 200:
                list_indexid_by_name = jq('.index_sets[].id',json.loads(response_getindexidbyname.text))
                # returns list of 1, convert to string and append to built in list of ids
                list_builtin_indexids.append("".join(list_indexid_by_name))
            else:
                exit_with_message(f"[ERROR] Couldn't find id. {str_index_name}",1)
    except requests.exceptions.RequestException as e:
        exit_with_message(f"[ERROR] Request error in get_list_all_builtin_index_set_ids: {e}",1)
    except ValueError as e:
        exit_with_message(f"[ERROR] JSON decoding error in get_list_all_builtin_index_set_ids: {e}",1)
    return list_builtin_indexids

def gen_list_index_set_names_to_delete(str_indexsets_url :str, dict_get_headers :dict,
    list_index_set_ids_to_delete: list) -> list:
    """src.clean.gen_list_index_set_names_to_delete function"""
    list_index_set_names_to_delete = []
    try:
        for str_index_id in list_index_set_ids_to_delete:
            str_get_index_set_name_byid_url = str_indexsets_url + "/" + str_index_id # get indexset by id filter out name
            response_get_index_set_name_byid = requests.get(str_get_index_set_name_byid_url, headers=dict_get_headers, timeout=3)
            response_get_index_set_name_byid.raise_for_status()
            if response_get_index_set_name_byid.status_code == 200:
                list_index_set_names = jq('.title',json.loads(response_get_index_set_name_byid.text))
                # returns list of 1, convert to string and append to built in list of ids
                list_index_set_names_to_delete.append("".join(list_index_set_names))
            else:
                exit_with_message(f"[ERROR] Couldn't find id. {str_index_id}",1)
    except requests.exceptions.RequestException as e:
        exit_with_message(f"[ERROR] Request error in gen_list_index_set_names_to_delete: {e}",1)
    except ValueError as e:
        exit_with_message(f"[ERROR] JSON decoding error in gen_list_index_set_names_to_delete: {e}",1)
    return list_index_set_names_to_delete

def remove_indexsets(bool_verbose :bool, str_indexsets_url :str, dict_get_headers :dict, dict_post_headers :dict,
    list_builtin_index_names :list) -> bool:
    """src.clean.remove_indexsets function"""
    list_all_index_set_ids = [] # all index_set ids
    list_builtin_index_set_ids = [] # all builtin index_set ids
    list_index_set_ids_to_delete = [] # index_set ids without builtin list
    list_index_set_names_to_delete = [] # names list without built ins

    print("Processing index sets for deletion")
    list_all_index_set_ids = get_list_all_index_sets_ids(str_indexsets_url, dict_get_headers)
    if len(list_all_index_set_ids) < 4:
        if bool_verbose:
            print("No index sets to delete")
        print("[Done] processing index sets for deletion.\n")
        return True
    list_builtin_index_set_ids = get_list_all_builtin_index_set_ids(str_indexsets_url,dict_get_headers,list_builtin_index_names)
    list_index_set_ids_to_delete = get_clean_list_ids_to_delete(list_all_index_set_ids,list_builtin_index_set_ids)
    if bool_verbose:
        print(f"{len(list_index_set_ids_to_delete)} Index Sets found")
    list_index_set_names_to_delete = gen_list_index_set_names_to_delete(str_indexsets_url,
        dict_get_headers,list_index_set_ids_to_delete)
    if bool_verbose:
        print(f"Removing IndexSet Ids {list_index_set_ids_to_delete}")
        print(f"Removing IndexSet Titles {list_index_set_names_to_delete}")
    for str_indexset_id in list_index_set_ids_to_delete:
        try:
            str_delete_index_set_byid_url = str_indexsets_url + "/" + str_indexset_id
            response_delete_index_set = requests.delete(str_delete_index_set_byid_url,
                headers=dict_post_headers, timeout=3)
            response_delete_index_set.raise_for_status()
            if not response_delete_index_set.status_code == 204:
                exit_with_message(f"[ERROR] Failed to delete input: {str_indexset_id}",1)
        except requests.exceptions.RequestException as e:
            exit_with_message(f"[ERROR] Request error in remove_indexsets: {e}",1)
        except ValueError as e:
            exit_with_message(f"[ERROR] JSON decoding error in remove_indexsets: {e}",1)
    print("[Done] processing index sets for deletion.\n")
    return True
