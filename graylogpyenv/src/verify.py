"""src.verify module"""
# from pyenv
import os
import json
from pathlib import Path
from jqpy import jq
from jsonschema import validate
from jsonschema.exceptions import ValidationError

# from source
from src.helpers import exit_with_message
from src.helpers import is_json_valid

def get_config_counts(bool_verbose :bool, list_config_directories :list,
    str_pth_host_cfg_dir :str, str_pth_host_cfg_template :str, str_pth_extrctr_cfg :str,
    str_pth_indices_cfg :str, str_pth_inputs_cfg :str, str_pth_streams_cfg :str,
    str_pth_schemas :str) -> int:
    """src.verify.get_config_counts function"""
    int_cfg_dir_count = len(list_config_directories) # get count of data dirs
    try:
        # get count of files per dir
        int_host_cfg_file_count = len(os.listdir(str_pth_host_cfg_dir))
        int_host_cfg_template_count = len(os.listdir(str_pth_host_cfg_template))
        int_xtrctr_cfg_file_count = len(os.listdir(str_pth_extrctr_cfg))
        int_indx_cfg_file_count = len(os.listdir(str_pth_indices_cfg))
        int_inpt_cfg_file_count = len(os.listdir(str_pth_inputs_cfg))
        int_strm_cfg_file_count = len(os.listdir(str_pth_streams_cfg))
        int_schema_file_count = len(os.listdir(str_pth_schemas))
        # sum counts for total
        int_total_file_count = ( int_host_cfg_file_count + int_host_cfg_template_count +
            int_xtrctr_cfg_file_count + int_indx_cfg_file_count + int_inpt_cfg_file_count +
            int_strm_cfg_file_count + int_schema_file_count )
        # print table so user can sanity check
        if bool_verbose:
            print(f"{int_cfg_dir_count} Data Dirs")
            print(f"{int_schema_file_count} Schema files")
            print(f"{int_host_cfg_file_count} Host cfg files")
            print(f"{int_host_cfg_template_count} Host cfg templates")
            print(f"{int_indx_cfg_file_count} Index config files")
            print(f"{int_inpt_cfg_file_count} Input config files")
            print(f"{int_strm_cfg_file_count} Stream config files")
            print(f"{int_xtrctr_cfg_file_count} Extractor config files\n")
    except os.error as e:
        exit_with_message(f"[ERROR] An OSError occurred in get_config_counts: {e}",1)
    return int_total_file_count

def verify_dirs_files_json(bool_verbose :bool, list_config_directories :list) -> int:
    # check config directory paths exists and is a directory in list items
    # build path to config file in directory
    # check built path to file is actually a file,
    # check has .json extension, and passed json decode test
    # exit if we fail a test (json is easy to mess up, lets fail early and fast)
    """src.verify.verify_dirs_files_json function"""
    str_config_dir = "" # loop var contains current dir being checked
    str_config_file = "" # loop var contains current config file being checked
    str_config_file_path = "" # built path to a config file
    int_config_file_count = 0
    try:
        for str_config_dir in list_config_directories:
            if bool_verbose:
                print(f"Validating data directory:{str_config_dir}")
            if not os.path.isdir(str_config_dir): # Check directory exist and is directory
                exit_with_message(f"[ERROR] {str_config_dir} Doesn't exist, or not a dir.",1)
            # Check config or schema file exists as a file, has json extension,
            # and it passes json validity check
            for str_config_file in os.listdir(str_config_dir):
                str_config_file_path = os.path.join(str_config_dir,str_config_file)
                if bool_verbose:
                    print(f"  Validating file:{str_config_file_path}")
                if not os.path.isfile(str_config_file_path):
                    exit_with_message(f"[ERROR] {str_config_file_path} is not a valid file.",1)
                if Path(str_config_file_path).suffix != ".json":
                    exit_with_message(f"[ERROR] {str_config_file_path} no .json extension.",1)
                if not is_json_valid(str_config_file_path):
                    exit_with_message(f"[ERROR] {str_config_file_path} failed json decode.",1)
                int_config_file_count += 1
    except os.error as e:
        exit_with_message(f"[ERROR] An OSError occurred in verify_dirs_files_json: {e}",1)
    return int_config_file_count

def verify_configfiles_filesystem(global_vars_list :list) -> None:
    """src.verify.verify_configfiles_filesystem function"""
    # keep count of total config files, directories
    # check schemas aren't writable, if they are this will
    # let you know something has potentially changed and needs validation
    # changing schema should require extra step to make file writable
    bool_verbose = global_vars_list[0]
    list_config_directories = global_vars_list[1]
    str_pth_host_cfg_dir = global_vars_list[2]
    str_pth_host_cfg_template = global_vars_list[3]
    str_pth_extrctr_cfg = global_vars_list[4]
    str_pth_indices_cfg = global_vars_list[5]
    str_pth_inputs_cfg = global_vars_list[6]
    str_pth_streams_cfg = global_vars_list[7]
    str_pth_schemas = global_vars_list[8]

    print("Verifying config files, schema, and data directories")
    try:
        int_total_file_count = get_config_counts(bool_verbose, list_config_directories,
            str_pth_host_cfg_dir, str_pth_host_cfg_template, str_pth_extrctr_cfg,
            str_pth_indices_cfg, str_pth_inputs_cfg, str_pth_streams_cfg, str_pth_schemas)
        int_config_file_count = verify_dirs_files_json(bool_verbose, list_config_directories)
        if int_config_file_count != int_total_file_count:
            exit_with_message("[ERROR] Config, schema files counted didn't match verified",1)
        for file in os.listdir(str_pth_schemas):
            if os.access(os.path.join(str_pth_schemas,file),os.W_OK):
                exit_with_message(f"[ERROR] {os.path.join(str_pth_schemas,file)} is writable.",1)
        print("[Done] Verifying config files, schema, and data directories\n")
    except os.error as e:
        exit_with_message(f"[ERROR] An OSError occurred in verify_configfiles_filesystem: {e}",1)

def verify_hostconfigfiles_schema(bool_verbose :bool, str_pth_host_cfg_dir :str,
        str_pth_host_schema :str) -> None:
    """src.verify.verify_hostconfigfiles_schema function"""
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

    print("Verifying schema of host configuration files.")
    try:
        int_count_hostcfg_files = len(os.listdir(str_pth_host_cfg_dir))
        if bool_verbose:
            print(f"  Host config directory: {str_pth_host_cfg_dir}")
            print(f"  Schema file: {str_pth_host_schema}")
            print(f"  {int_count_hostcfg_files} host config files found")
        for str_config_filename in os.listdir(str_pth_host_cfg_dir):
            int_config_set_count = 0
            int_actual_cs_count = 0
            str_host_config_file = os.path.join(str_pth_host_cfg_dir,str_config_filename)
            if bool_verbose:
                print(f"    Verifying schema of host config: {str_host_config_file}")
            with open(str_host_config_file, "r", encoding="utf-8") as configfile:
                dict_host_config=json.load(configfile)
            with open(str_pth_host_schema,"r", encoding="utf-8") as schemafile:
                dict_host_config_schema=json.load(schemafile)
            validate(instance=dict_host_config, schema=dict_host_config_schema)
            int_config_set_count = int(jq('.config_sets_total',dict_host_config,raw_output=True).text)
            int_actual_cs_count = len(jq('.config_sets[]',dict_host_config))
            str_config_hostname = str(jq('.hostname',dict_host_config,raw_output=True).text)
            if int_config_set_count != int_actual_cs_count:
                exit_with_message(f"[ERROR] Config sets declared:{int_config_set_count} Found:{int_actual_cs_count}",1)
            else:
                if bool_verbose:
                    print(f"     {int_config_set_count} config sets verified for host: {str_config_hostname}")
        print("[Done] Verifying schema of host configuration files\n")
    except os.error as e:
        exit_with_message(f"[ERROR] An OSError occurred in verify_hostconfigfiles_schema: {e}",1)
    except ValidationError as e:
        exit_with_message(f"[ERROR] Host config doesn't pass schema test: {e}",1)
    except json.JSONDecodeError as e:
        exit_with_message(f"[ERROR] There was a problem decoding json in verify_hostconfigfiles_schema: {e}",1)

def verify_hostconfig_subschema(bool_verbose: bool, file_loc: dict | str, str_pth_schema: str,
        str_pth_cfg: str) -> None:
    """src.verify.verify_hostconfig_subschema function"""
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

    if bool_verbose:
        print(f"    Verifying object(s): {file_loc}")
        print(f"      Using schema: {str_pth_schema}")
    try:
        for file in file_loc:
            str_filename=os.path.join(str_pth_cfg,file)
            if bool_verbose:
                print(f"      Checking: {str_filename}")
            with open(str_filename, "r", encoding="utf-8") as configfile:
                dict_input_config=json.load(configfile)
            with open(str_pth_schema,"r", encoding="utf-8") as schemafile:
                dict_input_schema=json.load(schemafile)
            validate(instance=dict_input_config, schema=dict_input_schema)
        if bool_verbose:
            print("      Object(s) align with schema.")
    except os.error as e:
        exit_with_message(f"[ERROR] An OSError occurred in verify_hostconfig_subschema: {e}",1)
    except json.JSONDecodeError as e:
        exit_with_message(f"[ERROR] Problem decoding json in verify_hostconfig_subschema: {e}",1)
    except ValidationError as e:
        exit_with_message(f"[ERROR] Doesn't pass schema test in verify_hostconfig_subschema: {e}",1)

def verify_hostconfigfiles_deps_schema(bool_verbose :bool, str_pth_host_cfg_dir :str,
        str_pth_schema_index :str, str_pth_indices_cfg :str, str_pth_schema_input :str,
        str_pth_inputs_cfg :str, str_pth_schema_stream, str_pth_streams_cfg :str,
        str_pth_schema_extractor :str, str_pth_extrctr_cfg :str) -> None:
    """src.verify.verify_hostconfigfiles_deps_schema function"""
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
    print("Analyzing host configuration file object's schema")
    try:
        for str_config_filename in os.listdir(str_pth_host_cfg_dir):
            str_config_file_path = os.path.join(str_pth_host_cfg_dir,str_config_filename)
            if bool_verbose:
                print(f"  Verifying host configuration file dependencies for: {str_config_file_path}")
            with open(str_config_file_path, "r", encoding="utf-8") as configfile:
                dict_host_config=json.load(configfile)
            dict_index_file_loc=jq('.config_sets[].index_config_file',dict_host_config)
            # for a host multiple config sets could use the same input remove dupes (only want to check input schema once)
            dict_input_file_loc=list(dict.fromkeys(jq('.config_sets[].input_config_file',dict_host_config)))
            dict_stream_file_loc=jq('.config_sets[].stream_config_file',dict_host_config)
            dict_extrctr_file_loc=jq('.config_sets[].extractors[].extractor_config_file',dict_host_config)
            verify_hostconfig_subschema(bool_verbose, dict_index_file_loc, str_pth_schema_index, str_pth_indices_cfg)
            verify_hostconfig_subschema(bool_verbose, dict_input_file_loc, str_pth_schema_input, str_pth_inputs_cfg)
            verify_hostconfig_subschema(bool_verbose, dict_stream_file_loc, str_pth_schema_stream, str_pth_streams_cfg)
            # it's possible to not have an extractor defined, so if count is 0 skip verifying nothing...
            if not len(dict_extrctr_file_loc) == 0:
                verify_hostconfig_subschema(bool_verbose, dict_extrctr_file_loc, str_pth_schema_extractor, str_pth_extrctr_cfg)
            else:
                if bool_verbose:
                    print(f"    No extractors defined in{str_config_file_path}")
        print("[Done] Analyzing host configuration file object's schema.\n")
    except os.error as e:
        exit_with_message(f"[ERROR] An OSError occurred in verify_hostconfigfiles_deps_schema: {e}",1)
    except json.JSONDecodeError as e:
        exit_with_message(f"[ERROR] Problem decoding json in verify_hostconfigfiles_deps_schema: {e}",1)

def check_hostconfig_indexes_unique(bool_verbose :bool,int_config_set_count :int, dict_host_config :dict
        , str_config_file_path :str) -> None:
    """src.verify.check_hostconfig_indexes_unique function"""
    # get list of all index config files, remove dupes.
    # If new list count is less than declared count in the config file, that means a dupe was removed.
    list_config_set_index_files = jq('.config_sets[].index_config_file',dict_host_config)
    int_count_indx_config_file = len(list(set(list_config_set_index_files)))
    if int_count_indx_config_file != int_config_set_count:
        exit_with_message(f"[ERROR] Duplicate indexes in host config file:{str_config_file_path}",1)
    else:
        if bool_verbose:
            print(f"    {int_count_indx_config_file} Unique indexes defined in: {str_config_file_path}")

def check_hostconfig_streams_unique(bool_verbose :bool, int_config_set_count :int, dict_host_config :dict
        ,str_config_file_path :str) -> None:
    """src.verify.check_hostconfig_streams_unique function"""
    # check stream config file is unique for each config set
    list_config_set_stream_files = jq('.config_sets[].stream_config_file',dict_host_config)
    int_count_strm_config_file = len(list(set(list_config_set_stream_files)))
    if int_count_strm_config_file != int_config_set_count:
        exit_with_message(f"[ERROR] Duplicate streams in host config file {str_config_file_path}",1)
    else:
        if bool_verbose:
            print(f"    {int_count_strm_config_file} Unique streams defined in:{str_config_file_path}")

def check_hostconfig_xtrctrs_unique(bool_verbose :bool, dict_host_config :dict, str_config_file_path :str) -> None:
    """src.verify.check_hostconfig_xtrctrs_unique function"""
    # Verify count of extractors in host config matches number statically defined
    # first add up all statically defined counts in each host file
    list_counts_xtrctr_config_file = jq('.config_sets[].extractors_total',dict_host_config)
    int_sum_of_extractors_count = 0
    for count in list_counts_xtrctr_config_file:
        int_sum_of_extractors_count = int_sum_of_extractors_count + count
    # get list of counts of extractors and sum the counts
    list_xtrctr_defs = jq('.config_sets[].extractors',dict_host_config)
    int_sum_of_defined_extractors_parsed = 0
    for xtrctr_list in list_xtrctr_defs:
        int_sum_of_defined_extractors_parsed = int_sum_of_defined_extractors_parsed + len(xtrctr_list)
    if int_sum_of_extractors_count != int_sum_of_defined_extractors_parsed:
        exit_with_message(f"[ERROR] Defined extractors != parsed extractors in host file {str_config_file_path}",1)
    else:
        if bool_verbose:
            print(f"    {int_sum_of_extractors_count} Unique extractors defined in: {str_config_file_path}")

def verify_hostconfig_integrity(bool_verbose :bool, str_pth_host_cfg_dir :str) -> None:
    """src.verify.verify_hostconfig_integrity function"""
    # build path to each config file in the directory
    # check index object files are unique (should be one index for every stream)
    # check stream object files are unique (should be one stream for every index)
    # check static declared count of extractors matches number of extractors defined
    # exit if any of the tests fail
    int_config_set_count = 0                    # value config_sets_total statically defined in config file
    str_config_filename = ""                    # loop variable containing filename found in directory
    str_config_file_path = ""                   # built path to file
    dict_host_config = {}                       # json content of config file

    print(f"Checking host configurations data integrity in directory: {str_pth_host_cfg_dir}")
    try:
        for str_config_filename in os.listdir(str_pth_host_cfg_dir):
            str_config_file_path = os.path.join(str_pth_host_cfg_dir,str_config_filename)
            with open(str_config_file_path, "r", encoding="utf-8") as configfile:
                dict_host_config=json.load(configfile)
            if bool_verbose:
                print(f"  Checking host config file: {str_config_file_path}")
            int_config_set_count = int(jq('.config_sets_total',dict_host_config,raw_output=True).text)
            check_hostconfig_indexes_unique(bool_verbose,int_config_set_count,dict_host_config,str_config_file_path)
            check_hostconfig_streams_unique(bool_verbose,int_config_set_count,dict_host_config,str_config_file_path)
            check_hostconfig_xtrctrs_unique(bool_verbose,dict_host_config,str_config_file_path)
        print("[Done] Checking host config file data integrity.\n")
    except os.error as e:
        exit_with_message(f"[ERROR] An OSError occurred in verify_hostconfig_integrity: {e}",1)
    except json.JSONDecodeError as e:
        exit_with_message(f"[ERROR] Problem decoding json in verify_hostconfig_integrity: {e}",1)

def get_hostname_from_config(bool_verbose :bool, str_config_filename :str, dict_host_config :dict) -> str:
    """src.verify.get_hostname_from_config function"""
    list_config_hostname = jq('.hostname',dict_host_config,raw_output=True)
    # host.domain.com is expectation
    str_parsed_host = list_config_hostname.text.split(".",maxsplit=1)
    str_clean_hostname=str_parsed_host[0].strip('"')
    if bool_verbose:
        print(f"  Checking host config: {str_config_filename} contains: {str_clean_hostname}")
    return str_clean_hostname

def check_index_title(bool_verbose :bool, str_hostname :str, dict_host_config :dict) -> None:
    """src.verify.check_index_title function"""
    # check object filenames and title have hostname somewhere in the string
    list_index_file_loc=jq('.config_sets[] | .index_config_file, .index_title',dict_host_config)
    if bool_verbose:
        print("    Checking index title")
    for title in list_index_file_loc:
        if not str_hostname in title:
            exit_with_message(f"[ERROR] {str_hostname} not found in object title {title}",1)

def check_input_title(bool_verbose :bool, str_hostname :str, dict_host_config :dict) -> None:
    """src.verify.check_input_title function"""
    # for a host multiple config sets could use the same input remove dupes
    list_input_file_loc=list(dict.fromkeys(jq('.config_sets[] | .input_config_file, .input_title',dict_host_config)))
    if bool_verbose:
        print("    Checking input title")
    for title in list_input_file_loc:
        if not str_hostname in title:
            exit_with_message(f"[ERROR] {str_hostname} not found in object file name or object title {title}",1)

def check_stream_title(bool_verbose :bool, str_hostname :str, dict_host_config :dict) -> None:
    """src.verify.check_stream_title function"""
    list_stream_file_loc=jq('.config_sets[] | .stream_config_file, .stream_title',dict_host_config)
    if bool_verbose:
        print("    Checking stream title")
    for title in list_stream_file_loc:
        if not str_hostname in title:
            exit_with_message(f"[ERROR] {str_hostname} not found in object file name or object title {title}",1)

def check_xtrctr_title(bool_verbose :bool, str_config_filename :str, str_hostname :str, dict_host_config :dict) -> None:
    """src.verify.check_xtrctr_title function"""
    # not all hosts inputs have extractors check if result is empty before runnng check
    list_extrctr_file_loc=jq('.config_sets[] | .extractors[] | .extractor_config_file',dict_host_config)
    # it's possible to have no extractor defined if not don't try
    if list_extrctr_file_loc == 0 and bool_verbose:
        print(f"    No extractors defined for host: {str_config_filename}")
    else:
        if bool_verbose:
            print("    Checking extractor title(s)")
        for title in list_extrctr_file_loc:
            if not str_hostname in title:
                exit_with_message(f"[ERROR] {str_hostname} not found in extractor file name {title}",1)

def verify_hostname_in_config(bool_verbose :bool, str_pth_host_cfg_dir :str, ) -> None:
    """src.verify.verify_hostname_in_config function"""
    # Check for title in host config matches named object files
    # In the case of extractors, the hostname is in the extractor filename not the definition itself
    # Get list of host config files in dir
    # Loop through list of host configs and store each object's file list in a dictionary
    # Parse out hostname from config
    # Loop through each dictionary of items and see if hostname is somewhere in the string
    str_config_filename = ""  # loop var containing just filename of host config
    str_config_file_path = "" # build full fs path to config file
    dict_host_config = {} # contains full config file loaded as json

    print("Checking hostname is present in object filenames and titles")
    try:
        for str_config_filename in os.listdir(str_pth_host_cfg_dir):
            str_config_file_path = os.path.join(str_pth_host_cfg_dir,str_config_filename)
            with open(str_config_file_path, "r", encoding="utf-8") as configfile:
                dict_host_config=json.load(configfile)
            str_hostname = get_hostname_from_config(bool_verbose,str_config_filename,dict_host_config)
            check_index_title(bool_verbose,str_hostname,dict_host_config)
            check_input_title(bool_verbose,str_hostname,dict_host_config)
            check_stream_title(bool_verbose,str_hostname,dict_host_config)
            check_xtrctr_title(bool_verbose,str_config_filename,str_hostname,dict_host_config)
        print("[Done] Checking hostname is present in object filenames and titles.\n")
    except os.error as e:
        exit_with_message(f"[ERROR] An OSError occurred in verify_hostname_in_config: {e}",1)
    except json.JSONDecodeError as e:
        exit_with_message(f"[ERROR] Problem decoding json in verify_hostname_in_config: {e}",1)

def verify_stream_rules(bool_verbose :bool, str_pth_host_cfg_dir :str, str_pth_streams_cfg :str) -> None:
    """src.verify.verify_stream_rules function"""
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
    dict_host_config = {}             # json dict of loaded host config file
    dict_stream_config = {}           # json dict of loaded stream config file
    list_config_sets = []             # list of config sets from jq query of host config file dictionary

    print("Checking stream rules have valid input static fields")
    try:
        # get list of all host config filenames
        for str_config_filename in os.listdir(str_pth_host_cfg_dir):
            # build full path to config file
            str_host_config_file = os.path.join(str_pth_host_cfg_dir,str_config_filename)
            if bool_verbose:
                print(f"  Host config: {str_host_config_file}")
            # load configfile into dictionary
            with open(str_host_config_file, "r", encoding="utf-8") as hostconfigfile:
                dict_host_config=json.load(hostconfigfile)
            # store list of config sets found in the dictionary
            list_config_sets = jq('.config_sets[]',dict_host_config)
            for config_set in list_config_sets:
                # get input title and stream config filename
                str_input_title = config_set["input_title"]
                str_stream_config_filename = config_set["stream_config_file"]
                if bool_verbose:
                    print(f"    Checking stream config file: {str_stream_config_filename}")
                # get full path to stream config file
                str_path_stream_configfile = os.path.join(str_pth_streams_cfg,str_stream_config_filename)
                # load stream configfile to dictionary
                with open(str_path_stream_configfile, "r", encoding="utf-8") as streamconfigfile:
                    dict_stream_config=json.load(streamconfigfile)
                # get input rule's static field name value
                jq_filter = '.rules[] | select(.field=="input") | .value'
                str_input_rule = jq(jq_filter,dict_stream_config,raw_output=True).text.strip('"')
                # do comparison
                if not str_input_title == str_input_rule:
                    exit_with_message(f"[ERROR] input title {str_input_title} != input name in {str_input_rule}",1)
        print("[Done] Checking stream rules have valid input static fields.\n")
    except os.error as e:
        exit_with_message(f"[ERROR] An OSError occurred in verify_stream_rules: {e}",1)
    except json.JSONDecodeError as e:
        exit_with_message(f"[ERROR] Problem decoding json in verify_stream_rules: {e}",1)
