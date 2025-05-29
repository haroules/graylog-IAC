# from pyenv
import sys
import os
import json
from jqpy import jq
from pathlib import Path
from jsonschema import validate
from jsonschema.exceptions import ValidationError

# from source
import graylog_global_vars
from src.graylog_helpers import exit_with_message
from src.graylog_helpers import is_json_valid

def verify_configfiles_filesystem():
    # load strings of directory paths to single list
    # check config directory paths exists and is a directory in list items
    # build path to config file in directory
    # check built path to file is actually a file, check has .json extension, and passed json decode test
    # exit if we fail a test (json is easy to mess up, lets fail early and fast)
    # keep count of total config files, directories
    str_config_dir = "" # loop var contains current dir being checked
    str_config_file = "" # loop var contains current config file being checked
    str_config_file_path = "" # built path to a config file
    int_config_file_count = 0 # total count of config files
    int_cfg_dir_count = 0 # total count of config directories

    print("Verifying config files, schema, and data directories")
    try:
        # get count of data dirs
        int_cfg_dir_count = len(graylog_global_vars.list_config_directories)
        # get count of files per dir
        int_host_cfg_file_count = len(os.listdir(graylog_global_vars.str_pth_host_cfg_dir))
        int_host_cfg_template_count = len(os.listdir(graylog_global_vars.str_pth_host_cfg_template))
        int_xtrctr_cfg_file_count = len(os.listdir(graylog_global_vars.str_pth_extrctr_cfg))
        int_indx_cfg_file_count = len(os.listdir(graylog_global_vars.str_pth_indices_cfg))
        int_inpt_cfg_file_count = len(os.listdir(graylog_global_vars.str_pth_inputs_cfg))
        int_strm_cfg_file_count = len(os.listdir(graylog_global_vars.str_pth_streams_cfg))
        int_schema_file_count = len(os.listdir(graylog_global_vars.str_pth_schemas))
        # sum counts for total
        int_total_file_count = ( int_host_cfg_file_count + int_host_cfg_template_count + 
              int_xtrctr_cfg_file_count + int_indx_cfg_file_count + int_inpt_cfg_file_count +
              int_strm_cfg_file_count + int_schema_file_count )
        
        # print table so user can sanity check
        if(graylog_global_vars.bool_verbose): print(int_cfg_dir_count,"Data Directories\t", int_schema_file_count, "Schema validation files")
        if(graylog_global_vars.bool_verbose): print(int_host_cfg_file_count,"Host config files\t", int_host_cfg_template_count, "Host config templates")
        if(graylog_global_vars.bool_verbose): print(int_indx_cfg_file_count, "Index config files\t", int_inpt_cfg_file_count, "Input config files")
        if(graylog_global_vars.bool_verbose): print(int_strm_cfg_file_count, "Stream config files\t", int_xtrctr_cfg_file_count, "Extractor config files") 
        
        # Check directory exist and is directory
        for str_config_dir in graylog_global_vars.list_config_directories:
            if(graylog_global_vars.bool_verbose): print("  Validating data directory:",str_config_dir)
            if not os.path.isdir(str_config_dir):
                print("[Error] Directory", str_config_dir, "Either doesn't exist, or is not a directory. Exiting.")
                sys.exit(1)
            # Check config or schema file exists as a file, has json extension, and is passes json validity check 
            for str_config_file in os.listdir(str_config_dir):
                str_config_file_path = os.path.join(str_config_dir,str_config_file)
                if(graylog_global_vars.bool_verbose): print("    Validating file:",str_config_file_path)
                if( (not(os.path.isfile(str_config_file_path))) and (Path(str_config_file_path).suffix == ".json") and (is_json_valid(str_config_file_path)) ):
                    print("[Error] ",str_config_file_path, " is not a valid file, doesn't exist, no .json ext, or failed json decode test. Exiting.")
                    sys.exit(1)
                else:
                    int_config_file_count += 1
        if(int_config_file_count != int_total_file_count):
            exit_with_message("[Error] Config and schema files counted did not match number verified",1)

        # check schemas aren't writable, if they are this will let you know something has potentially changed and needs validation
        # changing schema should require extra step to make file writable, hence you'll be careful...
        for file in os.listdir(graylog_global_vars.str_pth_schemas):
            if os.access(os.path.join(graylog_global_vars.str_pth_schemas,file),os.W_OK):
                print("[Error] ", os.path.join(graylog_global_vars.str_pth_schemas,file), "is writable. Please verfy your schema files changes and make them readonly again")
                sys.exit(1)

    except os.error as e:
        print(f"[Error] An OSError occurred verifying config directories or files: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[Error] Unknown error occurred: {e}")
        sys.exit(1)
        
    print("[Done] Verifying config files, schema, and data directories\n")

def verify_hostconfigfiles_schema():
    # check that any object creation config files referenced in host config file exist
    # verify filesystem objects before we access them
    # verify host config file adheres to defined host schema using jsonschema module
    # verify config sets defined matches static count declared
    str_config_filename = "" # loop var containing list of files found in dir
    str_config_hostname = "" # hostname read from config file
    str_host_config_file = "" # built full path to config file found in directory
    dict_host_config = {} # json dict of data from config file
    dict_host_config_schema = {} # json dict of data from schema file
    int_count_hostcfg_files = 0 # count of host config files found in directory
    int_config_set_count = 0 # count of config sets found in config file
    int_actual_cs_count = 0 # count of length of array items returned by filter

    if(graylog_global_vars.bool_verbose): print("Verifying schema of host configuration files.") 
    try:
        int_count_hostcfg_files = len(os.listdir(graylog_global_vars.str_pth_host_cfg_dir))
        if(graylog_global_vars.bool_verbose): print("  Host config directory:",graylog_global_vars.str_pth_host_cfg_dir)
        if(graylog_global_vars.bool_verbose): print("  Schema file:", graylog_global_vars.str_pth_host_schema)
        if(graylog_global_vars.bool_verbose): print(" ",int_count_hostcfg_files, "host config files found")
        for str_config_filename in os.listdir(graylog_global_vars.str_pth_host_cfg_dir):
            int_config_set_count = 0
            int_actual_cs_count = 0
            str_host_config_file = os.path.join(graylog_global_vars.str_pth_host_cfg_dir,str_config_filename)
            if(graylog_global_vars.bool_verbose): print("    Verifying schema of host config",str_host_config_file)
            with open(str_host_config_file, "r") as configfile:
                dict_host_config=json.load(configfile)
            with open(graylog_global_vars.str_pth_host_schema,"r") as schemafile:
                dict_host_config_schema=json.load(schemafile)
            validate(instance=dict_host_config, schema=dict_host_config_schema)
            int_config_set_count = int(jq('.config_sets_total',dict_host_config,raw_output=True).text)
            int_actual_cs_count = len(jq('.config_sets[]',dict_host_config))
            str_config_hostname = str(jq('.hostname',dict_host_config,raw_output=True).text)
            if(int_config_set_count != int_actual_cs_count):
                print("[Error] Host config sets declared in file:", int_config_set_count, "Actually found:",int_actual_cs_count)
                sys.exit(1)
            else:
                if(graylog_global_vars.bool_verbose): print ("     ", int_config_set_count,"config sets verified for host:",str_config_hostname)
    
    except os.error as e:
        print(f"[Error] An OSError occurred verifying config directories or files: {e}")
        sys.exit(1)
    except ValidationError as e:
        print(f"[Error] Host config doesn't pass schema test: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[Error] There was a problem decoding json: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[Error] Unknown error occurred: {e}")
        sys.exit(1)

    if(graylog_global_vars.bool_verbose): print("[Done] Verifying schema of host configuration files\n")

def verify_hostconfig_subschema(file_loc: dict | str, str_pth_schema: str, str_pth_cfg: str):
    # argument 1 is an object filename in a config file 
    # argument 2 is a path to the schema that correlates to the object config file
    # argument 3 is the path to the object filename
    # confirm that the built path of file exists and is a file
    # load the content of the object's config file
    # load the content of the corresponding schema
    # validate the content passes schema check
    str_filename = ""  # contains full path to object config file built from function inputs
    configfile = "" # file object that contains config object data
    schemafile = "" # file object that contains object schema
    dict_input_config = {} # json of config object
    dict_input_schema = {} # json of schema 

    if(graylog_global_vars.bool_verbose): print("    Verifying object(s)",file_loc) 
    if(graylog_global_vars.bool_verbose): print("      Using schema",str_pth_schema)
    try:
        for file in file_loc:
            str_filename=os.path.join(str_pth_cfg,file)
            if(graylog_global_vars.bool_verbose): print("      Checking:",str_filename)
            with open(str_filename, "r") as configfile:
                dict_input_config=json.load(configfile)
            with open(str_pth_schema,"r") as schemafile:
                dict_input_schema=json.load(schemafile)
            validate(instance=dict_input_config, schema=dict_input_schema)
    except os.error as e:
        print(f"[Error] An OSError occurred verifying config directories or files: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[Error] There was a problem decoding json: {e}")
        sys.exit(1)
    except ValidationError as e:
        print(f"[Error] Dependency config doesn't pass schema test: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[Error] Unknown error occurred: {e}")
        sys.exit(1)    
    if(graylog_global_vars.bool_verbose): print("      Object(s) align with schema.")

def verify_hostconfigfiles_deps_schema():
    # argument 1 path to host configuration file folder
    # get list of host config files in folder
    # verify that built path is actually a file
    # open config file and store json content
    # use jq to parse out object config files in each host config set 
    # verify each object config file against relevant object schema file
    # exit if an object file doesn't pass schema validation
    str_config_filename = ""
    dict_host_config = {}
    dict_index_file_loc = {}
    dict_input_file_loc = {}
    dict_stream_file_loc = {}
    dict_extrctr_file_loc = {}

    # verify sub config files refrenced in host file
    if(graylog_global_vars.bool_verbose): print("Analyzing host configuration file object's schema")
    try:
        for str_config_filename in os.listdir(graylog_global_vars.str_pth_host_cfg_dir):
            str_config_file_path = os.path.join(graylog_global_vars.str_pth_host_cfg_dir,str_config_filename)
            if(graylog_global_vars.bool_verbose): print("  Verifying host configuration file dependencies for:",str_config_file_path)
            with open(str_config_file_path, "r") as configfile:
                dict_host_config=json.load(configfile)
            dict_index_file_loc=jq('.config_sets[].index_config_file',dict_host_config)
            # for a host multiple config sets could use the same input remove dupes (only want to check input schema once)
            dict_input_file_loc=list(dict.fromkeys(jq('.config_sets[].input_config_file',dict_host_config)))
            dict_stream_file_loc=jq('.config_sets[].stream_config_file',dict_host_config)
            dict_extrctr_file_loc=jq('.config_sets[].extractors[].extractor_config_file',dict_host_config)
            verify_hostconfig_subschema(dict_index_file_loc, graylog_global_vars.str_pth_schema_index, graylog_global_vars.str_pth_indices_cfg)
            verify_hostconfig_subschema(dict_input_file_loc, graylog_global_vars.str_pth_schema_input, graylog_global_vars.str_pth_inputs_cfg)
            verify_hostconfig_subschema(dict_stream_file_loc, graylog_global_vars.str_pth_schema_stream, graylog_global_vars.str_pth_streams_cfg)
            # it's possible to not have an extractor defined, so if count is 0 skip verifying nothing...
            if(not(len(dict_extrctr_file_loc) == 0)):
                verify_hostconfig_subschema(dict_extrctr_file_loc, graylog_global_vars.str_pth_schema_extractor, graylog_global_vars.str_pth_extrctr_cfg) 
            else:
                if(graylog_global_vars.bool_verbose): print("    No extractors defined in", str_config_file_path)
    except os.error as e:
        print(f"[Error] An OSError occurred verifying config directories or files: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[Error] There was a problem decoding json: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[Error] Unknown error occurred: {e}")
        sys.exit(1)
    if(graylog_global_vars.bool_verbose): print("[Done] Analyzing host configuration file object's schema.\n")

def verify_hostconfig_integrity():
    # build path to each config file in the directory 
    # check index object files are unique (should be one index for every stream)
    # check stream object files are unique (should be one stream for every index)
    # check static declared count of extractors matches number of extractors defined
    # exit if any of the tests fail
    int_config_set_count = 0                    # value config_sets_total statically defined in config file
    int_count_indx_config_file = 0              # count of index config files parsed from jq (duplicates removed)
    int_count_strm_config_file = 0              # count of stream config files parsed from jq
    int_sum_of_extractors_count = 0             # count of extractors parsed from jq
    int_sum_of_defined_extractors_parsed = 0    # sum total of extractors count from array analysis
    str_config_filename = ""                    # loop variable containing filename found in directory
    str_config_file_path = ""                   # built path to file 
    dict_host_config = {}                       # json content of config file
    list_counts_xtrctr_config_file = []         # count of extractors statically defined in config file
    list_xtrctr_defs = []                       # list of counts of extractors
    
    if(graylog_global_vars.bool_verbose): print("Checking host configurations data integrity in directory:",graylog_global_vars.str_pth_host_cfg_dir)
    try:
        for str_config_filename in os.listdir(graylog_global_vars.str_pth_host_cfg_dir):
            str_config_file_path = os.path.join(graylog_global_vars.str_pth_host_cfg_dir,str_config_filename)
            with open(str_config_file_path, "r") as configfile:
                dict_host_config=json.load(configfile)
            if(graylog_global_vars.bool_verbose): print("  Checking host config file", str_config_file_path)
            int_config_set_count = int(jq('.config_sets_total',dict_host_config,raw_output=True).text)
            # get list of all index config files, remove dupes.  
            # If new list count is less than declared count in the config file, that means a dupe was removed.
            if(graylog_global_vars.bool_verbose): print("    Checking index config files are unique for each configuration set")
            int_count_indx_config_file = len(list(set(jq('.config_sets[].index_config_file',dict_host_config))))
            if(int_count_indx_config_file != int_config_set_count):
                print("[Error] Must have been duplicate indexes defined in the host config file:", str_config_file_path)
                sys.exit(1)
            else:
                if(graylog_global_vars.bool_verbose): print("      ", int_count_indx_config_file, "Unique indexes defined in:", str_config_file_path )    
            # check stream config file is unique for each config set
            if(graylog_global_vars.bool_verbose): print("    Checking stream config files are unique for each configuration set")
            int_count_strm_config_file = len(list(set(jq('.config_sets[].stream_config_file',dict_host_config))))
            if(int_count_strm_config_file != int_config_set_count):
                print("[Error] Must have been duplicate streams defined in the host file", str_config_file_path)
                sys.exit(1)
            else:
                if(graylog_global_vars.bool_verbose): print("      ", int_count_strm_config_file, "Unique streams defined in:", str_config_file_path )    
            # Verify count of extractors in host config matches number statically defined
            # first add up all statically defined counts in each host file
            if(graylog_global_vars.bool_verbose): print("    Verifying static extractor count matches number of defined extractors")
            list_counts_xtrctr_config_file = jq('.config_sets[].extractors_total',dict_host_config)
            int_sum_of_extractors_count = 0
            for count in list_counts_xtrctr_config_file:
                int_sum_of_extractors_count = int_sum_of_extractors_count + count                
            # get list of counts of extractors and sum the counts
            list_xtrctr_defs = jq('.config_sets[].extractors',dict_host_config)
            int_sum_of_defined_extractors_parsed = 0
            for xtrctr_list in list_xtrctr_defs:
                int_sum_of_defined_extractors_parsed = int_sum_of_defined_extractors_parsed + len(xtrctr_list)
            if(int_sum_of_extractors_count != int_sum_of_defined_extractors_parsed):
                print("[Error] Statically defined count of extractors didn't match count of parsed extractors in the host file", str_config_file_path)
                sys.exit(1)
            else:
                if(graylog_global_vars.bool_verbose): print("      ", int_sum_of_extractors_count, "Unique extractors defined in:", str_config_file_path )    

    except os.error as e:
        print(f"[Error] An OSError occurred verifying config directories or files: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[Error] There was a problem decoding json: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[Error] Unknown error occurred: {e}")
        sys.exit(1)
    
    if(graylog_global_vars.bool_verbose): print("[Done] Checking host config file data integrity.\n")

def verify_hostname_in_config():
    # Check for title in host config matches named object files
    # In the case of extractors, the hostname is in the extractor filename not the definition itself
    # Get list of host config files in dir
    # Loop through list of host configs and store each object's file list in a dictionary
    # Parse out hostname from config
    # Loop through each dictionary of items and see if hostname is somewhere in the string
    str_config_filename = ""  # loop var containing just filename of host config
    str_config_file_path = "" # build full fs path to config file
    str_parsed_host = "" # contains hostname parsed from config file
    str_clean_hostname = "" # contains hostname with quotes stripped for easier comparison
    list_config_hostname = [] # contains jq query results returned as list
    list_index_file_loc = [] # contains jq query results of index config files
    list_input_file_loc = [] # contains jq query results of input config files
    list_stream_file_loc = [] # contains jq query results of stream config files
    list_extrctr_file_loc = []  # contains jq query results of extractor config file names
    dict_host_config = {} # contains full config file loaded as json 
    
    if(graylog_global_vars.bool_verbose): print("Checking hostname is present in object filenames and titles")
    try:
        for str_config_filename in os.listdir(graylog_global_vars.str_pth_host_cfg_dir):
            str_config_file_path = os.path.join(graylog_global_vars.str_pth_host_cfg_dir,str_config_filename)
            with open(str_config_file_path, "r") as configfile:
                dict_host_config=json.load(configfile)
            list_config_hostname = jq('.hostname',dict_host_config,raw_output=True)
            # host.domain.com is expectation
            str_parsed_host = list_config_hostname.text.split(".",maxsplit=1)
            str_clean_hostname=str_parsed_host[0].strip('"')
            if(graylog_global_vars.bool_verbose): print("  Checking host config:", str_config_filename, "contains:",str_clean_hostname)
            # check object filenames and title have hostname somewhere in the string
            list_index_file_loc=jq('.config_sets[] | .index_config_file, .index_title',dict_host_config)
            # for a host multiple config sets could use the same input remove dupes (only want to check input schema once)
            list_input_file_loc=list(dict.fromkeys(jq('.config_sets[] | .input_config_file, .input_title',dict_host_config)))
            list_stream_file_loc=jq('.config_sets[] | .stream_config_file, .stream_title',dict_host_config)
            # not all hosts inputs have extractors check if result is empty before runnng check
            list_extrctr_file_loc=jq('.config_sets[] | .extractors[] | .extractor_config_file',dict_host_config)
            if(graylog_global_vars.bool_verbose): print("    Checking index config file and index title")
            for title in list_index_file_loc:
                if(not(str_clean_hostname in title)):
                    print("[Error] ",str_clean_hostname,"not found in object file name or object title", title)
                    sys.exit(1)
            if(graylog_global_vars.bool_verbose): print("    Checking input config file and input title")
            for title in list_input_file_loc:
                if(not(str_clean_hostname in title)):
                    print("[Error] ",str_clean_hostname,"not found in object file name or object title", title)
                    sys.exit(1)
            if(graylog_global_vars.bool_verbose): print("    Checking stream config file and stream title")
            for title in list_stream_file_loc:
                if(not(str_clean_hostname in title)):
                    print("[Error] ",str_clean_hostname,"not found in object file name or object title", title)
                    sys.exit(1)
            # it's possible to have no extractor defined if not don't try
            if(not(len(list_extrctr_file_loc) == 0)):
                if(graylog_global_vars.bool_verbose): print("    Checking extractor config filename")
                for title in list_extrctr_file_loc:
                    if(not(str_clean_hostname in title)):
                        print("[Error] ",str_clean_hostname,"not found in extractor file name", title)
                        sys.exit(1)
            else:
                if(graylog_global_vars.bool_verbose): print("    No extractors defined for host:",str_config_filename)

    except os.error as e:
        print(f"[Error] An OSError occurred verifying config directories or files: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[Error] There was a problem decoding json: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[Error] Unknown error occurred: {e}")
        sys.exit(1)
    if(graylog_global_vars.bool_verbose): print("[Done] Checking hostname is present in object filenames and titles.\n")

def verify_stream_rules():
    # Check stream rules have correct static field input name in the rule
    # Get list of host config files in the directory
    # Build full path to host config file in the directory
    # Load host config file to a dictionary
    # jq query out the config sets store into a list
    # iterate on each config set in the list
    # get the input title, stream config filename
    # load stream config to a dictionary
    # jq query out rules field named input 
    # compare against expected title
    str_config_filename = ""          # loop variable of filename found in config directory
    str_host_config_file = ""         # full path to config file found in config directory
    str_input_title = ""              # input title parsed from config set
    str_stream_config_filename = ""   # stream config filename parsed from config set
    str_path_stream_configfile = ""   # full path to stream config file
    str_input_rule = ""               # input rule from jq query stripped down to a string
    # hostconfigfile = ""             TextIOWrapper[_WrappedBuffer]
    # streamconfigfile = ""           TextIOWrapper[_WrappedBuffer]
    dict_host_config = {}             # json dict of loaded host config file 
    dict_stream_config = {}           # json dict of loaded stream config file
    list_config_sets = []             # list of config sets from jq query of host config file dictionary

    if(graylog_global_vars.bool_verbose): print("Checking stream rules have valid input static fields")
    try:
        # get list of all host config filenames
        for str_config_filename in os.listdir(graylog_global_vars.str_pth_host_cfg_dir):
            # build full path to config file
            str_host_config_file = os.path.join(graylog_global_vars.str_pth_host_cfg_dir,str_config_filename)
            if(graylog_global_vars.bool_verbose): print("  Host config", str_host_config_file)
            # load configfile into dictionary
            with open(str_host_config_file, "r") as hostconfigfile:
                dict_host_config=json.load(hostconfigfile)
            # store list of config sets found in the dictionary
            list_config_sets = jq('.config_sets[]',dict_host_config)
            for config_set in list_config_sets:
                # get input title and stream config filename
                str_input_title = config_set["input_title"]
                str_stream_config_filename = config_set["stream_config_file"]
                if(graylog_global_vars.bool_verbose): print("    Checking stream config file:",str_stream_config_filename)
                # get full path to stream config file
                str_path_stream_configfile = os.path.join(graylog_global_vars.str_pth_streams_cfg,str_stream_config_filename)
                # load stream configfile to dictionary
                with open(str_path_stream_configfile, "r") as streamconfigfile:
                    dict_stream_config=json.load(streamconfigfile)
                # get input rule's static field name value
                str_input_rule = jq('.rules[] | select(.field=="input") | .value',dict_stream_config,raw_output=True).text.strip('"')
                # do comparison
                if(not str_input_title == str_input_rule):
                    print("[Error] input title",str_input_title,"doesn't match input name in rule",str_input_rule)                
                    sys.exit(1)
    except os.error as e:
        print(f"[Error] An OSError occurred verifying config directories or files: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[Error] There was a problem decoding json: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[Error] Unknown error occurred: {e}")
        sys.exit(1)
    if(graylog_global_vars.bool_verbose): print("[Done] Checking stream rules static fields.\n")

