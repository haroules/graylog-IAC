import sys
from src.graylog_setup import usage
from src.graylog_setup import check_args
from src.graylog_setup import create_indices
from src.graylog_setup import create_inputs
from src.graylog_setup import create_static_fields
from src.graylog_setup import create_extractors
from src.graylog_setup import create_streams
from src.graylog_helpers import check_graylog_baseurl
from src.graylog_helpers import check_api_token
from src.graylog_helpers import set_global_vars
from src.graylog_backup import make_config_backup
from src.graylog_verify import verify_configfiles_filesystem
from src.graylog_verify import verify_hostconfigfiles_schema
from src.graylog_verify import verify_hostconfigfiles_deps_schema
from src.graylog_verify import verify_hostconfig_integrity
from src.graylog_verify import verify_hostname_in_config
from src.graylog_verify import verify_stream_rules
import graylog_global_vars

#TODO add check to all functions to verify input type

if __name__ == "__main__":
    validargs = check_args(sys.argv)
    if(isinstance(validargs,str)):    
        print(validargs)
        usage()
    set_global_vars(validargs)
    baseurlok=check_graylog_baseurl(validargs)
    if(isinstance(baseurlok,str)):
        print(baseurlok)
        sys.exit(1)
    tokenok=check_api_token([graylog_global_vars.str_cluster_url,graylog_global_vars.dict_get_headers])
    if(isinstance(tokenok,str)):
        print(tokenok)
        sys.exit(1)
    verify_configfiles_filesystem()
    verify_hostconfigfiles_schema()
    verify_hostconfigfiles_deps_schema()
    verify_hostconfig_integrity()
    verify_hostname_in_config()
    verify_stream_rules()
    # only make backup if all verify functions pass
    copyok=make_config_backup(validargs,graylog_global_vars.list_config_directories) 
    #create_indices()
    #create_inputs()
    #create_static_fields()
    #create_extractors()
    #create_streams()
