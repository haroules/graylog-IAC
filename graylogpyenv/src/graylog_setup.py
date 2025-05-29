# from pyenv
import os
from jqpy import jq
import json
import requests
import sys
from typing import Union
# from source
from src.graylog_helpers import exit_with_message
from src.graylog_helpers import contains_sublist
import graylog_global_vars

# pyjq doesn't compile for python3, jqpy python binding only has filter not replace
# going with pythonbinding vs systemcall
# sometimes its less code to use jq vs python dict elements (you will see both approaches used if your wonering why)

# TODO Create some bogus config files to test validate schema/integrity checks pickup errors
# TODO Create function to replace nodeid or indexid so we do it the same way, right now they're different
# TODO Verify all exception handlers and messages make sense/valid in function defs
# TODO Reduce amount of global variable usage and maybe shorten names for readability...
# TODO Reduce all the jq expressions to use json/dict search if it's simple or cleaner read

def usage():
    print("Usage: graylog-setup.py <admin token> <url> <verbose>")
    print("\t-Admin token and url are required, verbose defaults to True if not set (to False).")
    print("\t-Token should be 52 alpha-numeric characters.")
    print("\t-URL should be of the form http(s)://host|ip:port .")
    print("\t-Setting verbose to False will supress output.")
    sys.exit(1)

def check_args(args :list) -> Union[str, list[str,str,str,str], list[str,str,str,bool,str]]:
    # validate inputs to this script 
    # input to function is the arguments passed to the script at runtime
    # return args with current working directory appended or
    # return args with verbose flag set as bool and with current working directory appended
    print("Checking arguments and validating the inputs.")
    try:
        if ((len(args) < 3) or (len(args) > 4 )):   # check 2 or 3 args passed, argv has script name as arg so total should be 3 or 4
            return(f"[ERROR] Wrong number of script arguments. Number of args passed:{len(args) - 1}") 
        elif(len(args[1]) != 52):  # check token is 52 characters
            return(f"[ERROR] Token was wrong length. Length was:{len(args[1])}")            
        elif( not (args[1].isalnum())):  # check token is alpha numeric characters only
            return(f"[ERROR] Token had non alphanumeric characters.")
        # check optional Verbose flag set to true or false [case insensitive]
        elif(len(args) == 4):          # is there a third argument
            if( isinstance(args[3],str) and len(args[3]) > 3 and len(args[3]) < 6):  # must be string of 4 or 5 chars (true or false)
                str_arg_three = args[3].lower() # put string to all lower case to ease match 
                match str_arg_three:
                    case "true":
                        args[3]=True
                    case "false":
                        args[3]=False
                    case _:
                        return(f"[ERROR] Optional 3rd argument must be string: true or false.")
            else:
                return(f"[ERROR] Optional 3rd argument must be string: true or false.")
        # get current directory, and then get parent folder of that for cwd, then append path to args
        args.append(os.path.dirname(os.getcwd()))
        
    except Exception as e:
        print(f"[ERROR] Unknown error occurred in function checkargs: {e}")
        sys.exit(1)
    except os.error as e:
        print(f"[ERROR] An OSError occurred getting current working directory: {e}")
        sys.exit(1)

    print("[Done] Checking arguments and validating the inputs.\n")
    return(args)

def create_indices():
    # build list of definition files in directory and count them
    # exit if directory doesn't exist or minimal validation of config files fails
    # iterate over generated list creating index one at a time
    # function is idempotent since api/system won't allow you to create index dupes.
    # therefor we don't check to see if index already exists before trying to create it
    str_index_id = "" # id of created index parsed from json response
    str_index_name = ""  # title of created index parsed from json response
    str_index_file = "" # loop variable
    str_index_input_file = "" # loop variable
    str_index_file_path = "" # built path to index config file
    list_index_input_files = [] # list of paths for definition files
    int_index_file_count = 0 # count of create index files found 
    int_index_processed_count = 0 # count of index ops processed
    dict_index_config = {} # config file json 
    # index_post_response <class 'requests.models.Response'>

    print("Processing indexes")
    try:
        for str_index_file in os.listdir(graylog_global_vars.str_pth_indices_cfg):
            # build path to config files
            str_index_file_path = os.path.join(graylog_global_vars.str_pth_indices_cfg, str_index_file)
            list_index_input_files.append(str_index_file_path)
            int_index_file_count += 1
        # Verify index config check completed ok, later functions have dependencies on index names/ids. Exit on 0 found.
        if(int_index_file_count == 0):
            exit_with_message("[ERROR]  No config files found for creating indexes. Exiting.",1)
        else:
            if(graylog_global_vars.bool_verbose): print("  ", int_index_file_count, "Index config files to process.")
        # config files exist, now process the list of them    
        for str_index_input_file in list_index_input_files:
            if(graylog_global_vars.bool_verbose): print("    Creating index from config:", str_index_input_file)
            with open(str_index_input_file, "r") as file:
                dict_index_config = json.load(file) 
                index_post_response = requests.post(graylog_global_vars.str_indexsets_url, headers=graylog_global_vars.dict_post_headers, json=dict_index_config)
                match index_post_response.status_code:
                    case 400:
                        if(graylog_global_vars.bool_verbose): print("      Index already exists:",index_post_response.text)
                        int_index_processed_count += 1
                    case 200:
                        str_index_id = jq('.id',json.loads(index_post_response.text))
                        str_index_name = jq('.title',json.loads(index_post_response.text))
                        if(graylog_global_vars.bool_verbose): print("      Index:",str_index_name, "Id:",str_index_id, "was created")
                        int_index_processed_count += 1
                    case _:
                        print("[ERROR] Create index from file", str_index_input_file, "failed with error code:",index_post_response.status_code,"Message:",index_post_response.text)
                        sys.exit(1)
    except FileNotFoundError as e:
        print(f"Error: File or directory not found: {e}")
        sys.exit(1)
    except os.error as e:
        print(f"[ERROR] An OSError occurred verifying config directories or files: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERROR] There was a problem decoding json: {e}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unknown error occurred: {e}")
        sys.exit(1)
    # verify we did something for every index config file that exists
    if(int_index_file_count != int_index_processed_count):
        print("[ERROR] Processing indexes, config file count differed from processed count. File count:",int_index_file_count,"Processed count:",int_index_processed_count)
        sys.exit(1)
    else:
        print("[Done] processing indexes.\n")

def create_inputs():
    # copies of config file content could create havoc (two inputs with same config)
    # api/system won't stop you from re-creating inputs with the same name or configuration...
    # build list of definition files in directory and count them
    # exit if directory doesn't exist or minimal validation of config files fails
    # iterate over generated list creating inputs one at a time if they dont already exist
    int_input_file_count = 0 # count of input config files
    int_input_processed_count = 0 # count of created inputs
    str_input_file = "" # loop var
    str_input_file_path = "" # built path to input config file
    str_input_file_content = "" # json input config read in from file
    list_input_files = [] # path to each input definition file
    json_node_id = "" # json list node id from parse response
    titlesfound = [] # list of input titles that already exist
    input_name_json = "" # json input name
    # inputs_get_response = <class 'requests.models.Response'>
    # node_id_response <class 'requests.models.Response'>
    # inputs_post_response <class 'requests.models.Response'>

    print("Processing inputs")
    try:
        # get config files and store full path to file in a list
        for str_input_file in os.listdir(graylog_global_vars.str_pth_inputs_cfg):
            str_input_file_path = os.path.join(graylog_global_vars.str_pth_inputs_cfg, str_input_file)   
            list_input_files.append(str_input_file_path)
            int_input_file_count += 1
        # Verify input config checks completed ok, later functions have dependencies on inputs. Exit on 0 found.
        if(int_input_file_count == 0): exit_with_message("No config files found for creating inputs. Exiting",1)
        elif(graylog_global_vars.bool_verbose): print(" ",int_input_file_count, " input config files to process.")
        # get nodeid from api to replace in config files
        node_id_response = requests.get(graylog_global_vars.str_node_id_url, headers=graylog_global_vars.dict_get_headers) 
        if (node_id_response.status_code != 200):
            print("[ERROR] API call to:",graylog_global_vars.str_node_id_url,"Failed.")
            sys.exit(1)
        json_node_id = jq('.node_id',json.loads(node_id_response.text))
        # from list of input files paths, load content of file to var and replace node id in content
        # check if already exist, create if it doesn't
        if(graylog_global_vars.bool_verbose): print("  Replace nodeid:", json_node_id[0],"in input config files")
        for str_input_file_path in list_input_files:
            if(graylog_global_vars.bool_verbose): print("    Updating node id in:",str_input_file_path)
            with open(str_input_file_path, "r") as file:
                str_input_file_content = file.read()
            input_json_content = json.loads(str_input_file_content) # convert loaded file content to json
            input_name_json = jq('.title',input_json_content) # filter out title from content
            str_node_id = str(json_node_id[0])  # store title as string var
            # verify specific field exists
            if "node" in input_json_content:
                input_json_content["node"] = str_node_id  # replace existing node id with new one
                with open(str_input_file_path, "w") as file:  # write back to file
                    json.dump(input_json_content,file, indent=2)
            else:
                print("[ERROR] Couldn't update config file", str_input_file_path, "with", str_node_id)
                sys.exit(1)
            # create list of input titles that exist already
            inputs_get_response = requests.get(graylog_global_vars.str_inputs_url, headers=graylog_global_vars.dict_get_headers)
            titlesfound = jq('.inputs[].title',data=json.loads(inputs_get_response.text))
            # check if the input we want to create exists already
            if(contains_sublist(input_name_json,titlesfound)):
                if(graylog_global_vars.bool_verbose): print("   ",input_name_json," Input already exists, skipping creation")
                int_input_processed_count += 1
            else:  # input doesn't exist already, create input from file      
                inputs_post_response = requests.post(graylog_global_vars.str_inputs_url, headers=graylog_global_vars.dict_post_headers, json=input_json_content)
                match inputs_post_response.status_code:
                    case 201:
                        json_created_input_id = jq('.id',json.loads(inputs_post_response.text))
                        if(graylog_global_vars.bool_verbose): print("    InputTitle:",input_name_json,"InputID:",json_created_input_id, "Created ")
                        int_input_processed_count += 1
                    case _:
                        print("[ERROR] Create input failed with error code:",inputs_post_response.status_code,"Message:",inputs_post_response.text)
    except FileNotFoundError as e:
        print(f"Error: File or directory not found: {e}")
        sys.exit
    except FileNotFoundError as e:
        print(f"Error: File or directory not found: {e}")
        sys.exit
    except os.error as e:
        print(f"[ERROR] An OSError occurred verifying config directories or files: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERROR] There was a problem decoding json: {e}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unknown error occurred: {e}")
        sys.exit(1)

    # verify we did something for every input config file that exists
    if(int_input_file_count != int_input_processed_count ):
        print("[ERROR] processing inputs, config file count differed from processed count. Files:",int_input_file_count,"Processed:",int_input_processed_count)
    else:
        print("[Done] Processing inputs.\n")

def create_static_fields():
    # add static field to input
    # its an extra step which would be nice if we could include with the input creation json...
    # i used static field since i have multiple input(types) from the same host in my stream rules
    # get list of titles/ID's from api 
    # build json payload 
    # iterate through list add static field titled "input" that matches the "title of the input"
    # no need to check if static field already exists. it appears to overwrite based on evidence in logs
    # check count of inputs matches ceation count
    json_titles_found = "" # key/val pair of title/id
    str_static_field_url = "" # relative url for modify static fileld of input built on the fly
    json_static_payload = "" # jason payload describing static field built on the fly
    json_inputs_count = "" # count of inputs found parsing json response
    int_static_created_count = 0 # count of static fields created
    # get_inputs_response <class 'requests.models.Response'>
    # create_static_field_response <class 'requests.models.Response'>

    print("Processing static fields")
    try:
        get_inputs_response = requests.get(graylog_global_vars.str_inputs_url, headers=graylog_global_vars.dict_get_headers)
        json_inputs_count = int(jq('.total',data=json.loads(get_inputs_response.text),raw_output=True).text)
        if(graylog_global_vars.bool_verbose): print("  ",json_inputs_count,"Static fields to process.")
        # Need inputs, otherwise something wrong, won't be able to process other creations
        # unlikely to occur (previous steps would fail) 
        # someone edits ui while script processing and deletes inputs
        if(json_inputs_count == 0):
            exit_with_message("[ERROR] No inputs found. Exiting",1)
        json_titles_found = jq('.inputs[] | [ .title,.id ]',data=json.loads(get_inputs_response.text))
        for static_field_keypair in json_titles_found:
            str_static_field_url = graylog_global_vars.str_inputs_url + "/" + static_field_keypair[1] + "/staticfields"
            json_static_payload = '{"key":"input","value":"' + static_field_keypair[0] + '"}'
            create_static_field_response = requests.post(str_static_field_url, headers=graylog_global_vars.dict_post_headers, json=json.loads(json_static_payload))
            if(create_static_field_response.status_code != 201):
                print("[ERROR] Add static field failed with error code:",create_static_field_response.status_code,"Message:",create_static_field_response.text)
            else:
                if(graylog_global_vars.bool_verbose): print("  Static field added:", json_static_payload)
                int_static_created_count += 1

    except json.JSONDecodeError as e:
        print(f"[ERROR] There was a problem decoding json: {e}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unknown error occurred: {e}")
        sys.exit(1)
    
    # verify we created static field for every input we found
    if( json_inputs_count != int_static_created_count):
        print("Done creating static fields, inputs found count differed from created count. Input count:",json_inputs_count,"Created count:",int_static_created_count)
        sys.exit(1)
    else:
        print("[Done] Processing static fields.\n")

def create_extractors():
    # get list of extractors for an input from host config file
    # get count of extractors static defined
    # if extractor total for a config set is 0 skip 
    # if not get list of extractors and input title from config set
    # make sure doesn't already exist comparing against list that may already exist
    # host config file may have one or more config sets
    # each config set may have 0 or more extractors
    str_path_host_config_file = ""          # loop var config file name from directory listing
    str_full_pth_host_cfg_file = ""         # build full fs path to config file
    str_input_title = ""                    # get input title from jq query of config set
    str_jqfilter = ""                       # built jq query string that takes input id as variable
    str_inputid = ""                        # input id for extractor from jq query filtering by name from all inputs
    str_xtractr_url = ""                    # built url to get extractors for an input by input id
    str_xtrctr_title = ""                   # extractor title from jq query of extractor config file
    int_total_xtrctrs_in_configfile = 0     # sum total of extractors_count from all config sets     
    int_count_xtrctr_ops = 0                # incremented count of extractors added or checked already exist
    int_xtrctr_cfg_file_count = 0           # count of extractor config files on file system
    dict_host_config = {}                   # host config file loaded as json dictionary
    list_xtrctr_counts_in_configfile = []   # list of counts of extractors found in host config file
    list_config_sets = []                   # list of config sets found in host config file
    list_existing_xtrctr = []               # list of extractors that already exist retrieved from API
    list_extractors = []                    # sub list of extractors in each config set
    
    print("Processing extractors")
    int_xtrctr_cfg_file_count = len(os.listdir(graylog_global_vars.str_pth_extrctr_cfg))
    if(graylog_global_vars.bool_verbose): print("  ", int_xtrctr_cfg_file_count, "Extractors to process.")
    try: 
        # loop on list of host config files found in directory
        for str_path_host_config_file in os.listdir(graylog_global_vars.str_pth_host_cfg_dir):
            str_full_pth_host_cfg_file = os.path.join(graylog_global_vars.str_pth_host_cfg_dir,str_path_host_config_file)
            with open(str_full_pth_host_cfg_file, "r") as hostconfigfile:
                dict_host_config=json.load(hostconfigfile)
            int_total_xtrctrs_in_configfile = 0 
            # each config file may have multiple config sets so have to create a list of config counts
            list_xtrctr_counts_in_configfile=jq('.config_sets[].extractors_total',dict_host_config)
            for xtrctr_count_in_config_set in list_xtrctr_counts_in_configfile:
                int_total_xtrctrs_in_configfile += int(xtrctr_count_in_config_set)
            if(graylog_global_vars.bool_verbose): print("  ",str_full_pth_host_cfg_file, "has", int_total_xtrctrs_in_configfile,"extractors defined")
            list_config_sets=jq('.config_sets[]',dict_host_config)
            int_tot_xtrctrs_in_configset = 0
            for config_set in list_config_sets:
                # reset count of operations performed for each non empty list
                int_count_xtrctr_ops = 0
                # its possible that an extractor isn't configured for a config set, so get count for config set
                int_tot_xtrctrs_in_configset = int(jq('.extractors_total',config_set,raw_output=True).text)
                # if 0 extractors are found skip config set otherwise create or skip if already exists
                if(int_tot_xtrctrs_in_configset > 0):
                    str_input_title=jq('.input_title',config_set,raw_output=True).text
                    list_extractors=jq('.extractors[].extractor_config_file',config_set)
                    # get list of all inputs
                    get_inputs_response = requests.get(graylog_global_vars.str_inputs_url, headers=graylog_global_vars.dict_get_headers)
                    # build jq filter string to get id of input with title from variable
                    str_jqfilter = '.inputs[] | select(.title == ' + str_input_title + ') | .id'
                    # jq query to get input id from all inputs receieved from API
                    str_inputid = jq(str_jqfilter,data=json.loads(get_inputs_response.text),raw_output=True).text.strip('"')
                    for xtrctr in list_extractors:
                        # build url to query extractors of an input from its id
                        str_xtractr_url = graylog_global_vars.str_inputs_url + "/" + str_inputid + "/extractors"
                        get_xtractr_response = requests.get(str_xtractr_url, headers=graylog_global_vars.dict_get_headers)
                        # check if the response from input by id already has extractors defined in a list
                        with open(os.path.join(graylog_global_vars.str_pth_extrctr_cfg,xtrctr), "r") as file:   
                            str_xtrctr_title=jq('.title',data=json.load(file))
                        list_existing_xtrctr=jq('.extractors[].title',json.loads(get_xtractr_response.text))
                        # make sure extractors title isn't in the list we just got , add if they don't
                        if(contains_sublist(str_xtrctr_title,list_existing_xtrctr)):
                            if(graylog_global_vars.bool_verbose): print("     Extractor",str_xtrctr_title,"already exists")
                            # update count of extractors processed
                            int_count_xtrctr_ops += 1
                        else:    
                            if(graylog_global_vars.bool_verbose): print("     Creating extractor:",xtrctr, "for input", str_input_title, "with id", str_inputid)
                            with open(os.path.join(graylog_global_vars.str_pth_extrctr_cfg,xtrctr), "r") as xtrctr_config_file:
                                xtrctr_add_response = requests.post(str_xtractr_url, headers=graylog_global_vars.dict_post_headers,json=json.load(xtrctr_config_file))
                                # check if we were succesful in adding extractor to input
                                if(xtrctr_add_response.status_code != 201): # this seems goofy should success be 200
                                    print("[ERROR] Add extractor failed with error code:",xtrctr_add_response.status_code,"Message:",xtrctr_add_response.text)            
                                    sys.exit(1)
                                else:
                                    if(graylog_global_vars.bool_verbose): print("    Extractor added:",xtrctr_add_response.text)
                                    # update count of extractors processed
                                    int_count_xtrctr_ops += 1
                    # check that total count of extractors in config file matches number we iterated on
                    if(int_count_xtrctr_ops != int_tot_xtrctrs_in_configset):
                        print("[ERROR] Extractor operations performed:",int_count_xtrctr_ops, "was less than expected count:",int_tot_xtrctrs_in_configset )
    except FileNotFoundError as e:
        print(f"Error: File or directory not found: {e}")
        sys.exit
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        sys.exit(1)
    except os.error as e:
        print(f"[ERROR] An OSError occurred verifying config directories or files: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERROR] There was a problem decoding json: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unknown error occurred: {e}")
        sys.exit(1)
    print("[Done] processing extractors.\n")
    
def create_streams():
     # TODO comment variables
     # TODO comment function
     # TODO check errors for create/start stream
    str_path_host_config_file = ""
    str_pth_stream_config_file = ""
    str_searchindexsetbyname_url = ""
    indexset_id_response = ""
    dict_host_config = {}
    dict_stream_config = {}
    int_stream_tot_count = 0
    int_strm_cfg_file_count = 0
    stream_config_file = ""
    stream_response = ""
    create_stream_response = ""
    stream_title = ""
    stream_titles = ""
    index_title = ""
    json_indexset_id = ""
    new_stream_id = ""
    start_stream_response = ""
    start_stream_url = ""
    # hostconfigfile                TextIOWrapper[_WrappedBuffer]
    # streamconfigfile              TextIOWrapper[_WrappedBuffer]

    print("Processing streams")
    int_strm_cfg_file_count = len(os.listdir(graylog_global_vars.str_pth_streams_cfg))
    if(graylog_global_vars.bool_verbose): print(" ", int_strm_cfg_file_count, "Streams to process.")
    try: 
        for str_path_host_config_file in os.listdir(graylog_global_vars.str_pth_host_cfg_dir):
            str_full_pth_host_cfg_file = os.path.join(graylog_global_vars.str_pth_host_cfg_dir,str_path_host_config_file)
            if(graylog_global_vars.bool_verbose): print("  Creating streams defined in:",str_full_pth_host_cfg_file)
            with open(str_full_pth_host_cfg_file, "r") as hostconfigfile:
                dict_host_config=json.load(hostconfigfile)
            list_config_sets=jq('.config_sets[]',dict_host_config)
            for config_set in list_config_sets:
                stream_config_file = config_set["stream_config_file"]
                stream_title = config_set["stream_title"]
                index_title = config_set["index_title"]
                # multiple streams likely share an input, only want to get a list of uniqueinputs
                str_pth_stream_config_file = os.path.join(graylog_global_vars.str_pth_streams_cfg,stream_config_file)
                # get indexsetid from api to replace in config files
                str_searchindexsetbyname_url=graylog_global_vars.str_indexsets_url + "/search?searchTitle=" + index_title
                indexset_id_response = requests.get(str_searchindexsetbyname_url, headers=graylog_global_vars.dict_get_headers) 
                json_indexset_id = jq('.index_sets[].id',json.loads(indexset_id_response.text),raw_output=True).text.strip('"')
                # replace indexsetid in config file
                # todo make backup copy of files
                with open(str_pth_stream_config_file, "r") as streamconfigfile:
                    dict_stream_config=json.load(streamconfigfile)
                if "index_set_id" in dict_stream_config:
                    if(graylog_global_vars.bool_verbose): print("    Updating",str_pth_stream_config_file, "with index id",json_indexset_id )
                    dict_stream_config["index_set_id"] = json_indexset_id
                    with open(str_pth_stream_config_file, "w") as file:
                        json.dump(dict_stream_config,file, indent=2)
                else:
                    print("[ERROR] Couldn't update stream config file", str_pth_stream_config_file)
                    sys.exit(1)
                # check if stream already exists create otherwise and start
                stream_response=requests.get(graylog_global_vars.str_streams_url, headers=graylog_global_vars.dict_get_headers)
                stream_titles = jq('.streams[].title',json.loads(stream_response.text))                
                if(stream_title in stream_titles):
                    if(graylog_global_vars.bool_verbose): print("      Stream", stream_title, "Already exists")
                else:
                    if(graylog_global_vars.bool_verbose): print("      Create Stream",stream_title,"from config", stream_config_file)
                    with open(str_pth_stream_config_file, "r") as streamconfigfile:
                        dict_stream_config=json.load(streamconfigfile)
                    # create stream
                    create_stream_response=requests.post(graylog_global_vars.str_streams_url, headers=graylog_global_vars.dict_post_headers,json=dict_stream_config)
                    # get newly created stream id from return message
                    new_stream_id=jq('.stream_id',json.loads(create_stream_response.text),raw_output=True).text.strip('"')
                    # newly created streams don't autostart, so start stream
                    start_stream_url = graylog_global_vars.str_streams_url + "/" + new_stream_id + "/resume"
                    start_stream_response=requests.post(start_stream_url,headers=graylog_global_vars.dict_post_headers)
    except FileNotFoundError as e:
        print(f"Error: File or directory not found: {e}")
        sys.exit
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request error: {e}")
        sys.exit(1)
    except os.error as e:
        print(f"[ERROR] An OSError occurred verifying config directories or files: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERROR] There was a problem decoding json: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unknown error occurred: {e}")
        sys.exit(1)

    print("[Done] Processing streams.\n")
