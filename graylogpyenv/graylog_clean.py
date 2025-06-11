""" graylog_clean main module """
import sys
from src.helpers import do_init
from src.clean import remove_streams
from src.clean import remove_inputs
from src.clean import remove_indexsets
import global_vars

def main():
    """Function graylog_clean.main"""
    do_init(sys.argv)
    if not remove_streams(global_vars.BOOL_VERBOSE, global_vars.STR_STREAMS_URL, global_vars.DICT_GET_HEADERS,
        global_vars.DICT_POST_HEADERS, global_vars.LIST_BUILTIN_STREAMS_IDS):
        sys.exit(1)
    if not remove_inputs(global_vars.BOOL_VERBOSE, global_vars.STR_INPUTS_URL, global_vars.DICT_GET_HEADERS,
        global_vars.DICT_POST_HEADERS):
        sys.exit(1)
    if not remove_indexsets(global_vars.BOOL_VERBOSE, global_vars.STR_INDEXSETS_URL,global_vars.DICT_GET_HEADERS,
        global_vars.DICT_POST_HEADERS,global_vars.LIST_BUILTIN_INDEX_NAMES):
        sys.exit(1)
    print("Done removing streams, inputs, and index sets")

def init():
    """Function graylog_clean.init"""
    if __name__ == "__main__":
        sys.exit(main())
init()
