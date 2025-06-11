""" graylog_verify main module """

import sys
from src.verify import verify_configfiles_filesystem
from src.verify import verify_hostconfigfiles_schema
from src.verify import verify_hostconfigfiles_deps_schema
from src.verify import verify_hostconfig_integrity
from src.verify import verify_hostname_in_config
from src.verify import verify_stream_rules
from src.helpers import check_args_verify
from src.helpers import set_global_vars_verify
from src.helpers import usage
import global_vars

def main():
    """Function graylog_verify.main"""
    validargs = check_args_verify(sys.argv)
    if isinstance(validargs,str):
        print(validargs)
        usage(sys.argv)
        sys.exit(1)
    set_global_vars_verify(validargs)
    global_vars_list = [global_vars.BOOL_VERBOSE,
        global_vars.LIST_CONFIG_DIRECTORIES, global_vars.STR_PTH_HOST_CFG_DIR,
        global_vars.STR_PTH_HOST_CFG_TEMPLATE, global_vars.STR_PTH_EXTRCTR_CFG,
        global_vars.STR_PTH_INDICES_CFG, global_vars.STR_PTH_INPUTS_CFG,
        global_vars.STR_PTH_STREAMS_CFG, global_vars.STR_PTH_SCHEMAS]
    verify_configfiles_filesystem(global_vars_list)
    verify_hostconfigfiles_schema(global_vars.BOOL_VERBOSE,
        global_vars.STR_PTH_HOST_CFG_DIR, global_vars.STR_PTH_HOST_SCHEMA)
    verify_hostconfigfiles_deps_schema(global_vars.BOOL_VERBOSE,
        global_vars.STR_PTH_HOST_CFG_DIR, global_vars.STR_PTH_SCHEMA_INDEX,
        global_vars.STR_PTH_INDICES_CFG, global_vars.STR_PTH_SCHEMA_INPUT,
        global_vars.STR_PTH_INPUTS_CFG, global_vars.STR_PTH_SCHEMA_STREAM,
        global_vars.STR_PTH_STREAMS_CFG, global_vars.STR_PTH_SCHEMA_EXTRACTOR,
        global_vars.STR_PTH_EXTRCTR_CFG)
    verify_hostconfig_integrity(global_vars.BOOL_VERBOSE,
        global_vars.STR_PTH_HOST_CFG_DIR)
    verify_hostname_in_config(global_vars.BOOL_VERBOSE,
        global_vars.STR_PTH_HOST_CFG_DIR)
    verify_stream_rules(global_vars.BOOL_VERBOSE, global_vars.STR_PTH_HOST_CFG_DIR,
        global_vars.STR_PTH_STREAMS_CFG)

def init():
    """Function graylog_verify.init"""
    if __name__ == "__main__":
        sys.exit(main())
init()
