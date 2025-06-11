""" graylog_setup main module """

import sys
from src.setup import create_indices
from src.setup import create_inputs
from src.setup import create_static_fields
from src.setup import create_extractors
from src.setup import create_streams
from src.helpers import do_init
from src.backup import make_config_backup
import global_vars

def main():
    """Function graylog_setup.main"""
    validargs = do_init(sys.argv)
    make_config_backup(validargs,global_vars.LIST_CONFIG_DIRECTORIES)
    create_indices(global_vars.BOOL_VERBOSE,global_vars.STR_PTH_INDICES_CFG,
                   global_vars.STR_INDEXSETS_URL,global_vars.DICT_POST_HEADERS)
    create_inputs(global_vars.BOOL_VERBOSE,global_vars.STR_PTH_INPUTS_CFG,
                  global_vars.STR_NODE_ID_URL,global_vars.STR_INPUTS_URL,
                  global_vars.DICT_GET_HEADERS,global_vars.DICT_POST_HEADERS)
    create_static_fields(global_vars.BOOL_VERBOSE,global_vars.STR_INPUTS_URL,
                         global_vars.DICT_GET_HEADERS,global_vars.DICT_POST_HEADERS)
    create_extractors(global_vars.BOOL_VERBOSE,global_vars.STR_PTH_EXTRCTR_CFG,
                      global_vars.STR_PTH_HOST_CFG_DIR,global_vars.STR_INPUTS_URL,
                      global_vars.DICT_GET_HEADERS,global_vars.DICT_POST_HEADERS)
    create_streams(global_vars.BOOL_VERBOSE, global_vars.STR_PTH_STREAMS_CFG,
                   global_vars.STR_PTH_HOST_CFG_DIR, global_vars.STR_INDEXSETS_URL,
                   global_vars.STR_STREAMS_URL, global_vars.DICT_GET_HEADERS,
                   global_vars.DICT_POST_HEADERS)

def init():
    """Function graylog_setup.init"""
    if __name__ == "__main__":
        sys.exit(main())
init()
