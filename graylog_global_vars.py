# Define global variables
global str_admintoken           # admin token passed on CLI
global str_pth_cwd              # keep track of where we are on the fs
global bool_verbose             # suppress verbose output
global list_config_directories   # harcoded list of config and data directories

# URL global variables
global str_cluster_url      # URL of cluster API endpoint
global str_graylogbase_url  # URL of graylog instance we will operate on
global str_indexsets_url    # URL of index sets API endpoint
global str_inputs_url       # URL of inputs API endpoint
global str_node_id_url      # URL of API endpoint to get node id
global str_streams_url      # URL of streams API endpoint
# requests headers
global dict_get_headers     # dictionary of get headers supplied to get requests including auth
global dict_post_headers    # dictionary of post headers supplied to post requests including auth
# relative fs path of various object config files
global str_pth_host_cfg_dir
global str_pth_host_cfg_template
global str_pth_extrctr_cfg
global str_pth_indices_cfg
global str_pth_inputs_cfg
global str_pth_streams_cfg
# relative fs path to schema defining object configs
global str_pth_schemas
global str_pth_host_schema
global str_pth_schema_index 
global str_pth_schema_input 
global str_pth_schema_extractor 
global str_pth_schema_stream 

# intialize to empty - they get assigned in gralog_helpers:set_global_vars
bool_verbose = True
str_admintoken = ""  
str_pth_cwd = ""
str_pth_extrctr_cfg = ""
str_pth_host_cfg_dir = "" 
str_pth_host_cfg_template = "" 
str_pth_host_schema = ""
str_pth_indices_cfg = "" 
str_pth_inputs_cfg = "" 
str_pth_streams_cfg = "" 
str_pth_schemas = ""
str_pth_schema_index = ""
str_pth_schema_input = ""
str_pth_schema_extractor = ""
str_pth_schema_stream = ""
str_cluster_url = ""
str_graylogbase_url = "" 
str_indexsets_url = ""   
str_inputs_url = "" 
str_node_id_url = ""    
str_streams_url = "" 
dict_get_headers = {}  
dict_post_headers = {} 
list_config_directories = []