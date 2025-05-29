import os
import graylog_global_vars
from src.graylog_helpers import set_global_vars

VALID_SCRIPT = "graylog_setup.py"
VALID_TOKEN = "A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R8S9T0U1V2W3X4Y5Z6"  # A valid 52-char alphanumeric token
VALID_URL = "http://graylog.example.com"
VALID_CWD = os.path.dirname(os.getcwd())
VERBOSE = False

#TODO Validate "CWD" in tests

def test_set_global_vars_output_3_args(capsys):
    args = [VALID_SCRIPT, VALID_TOKEN, VALID_URL, VALID_CWD]
    set_global_vars(args)
    captured = capsys.readouterr()
    expected_output = (
        "Assigning global variables.\n"
        "[Done] Assigning global variables.\n\n"
    )
    assert captured.out == expected_output
    assert graylog_global_vars.bool_verbose == True
    assert graylog_global_vars.str_inputs_url == VALID_URL + "/system/inputs"
    assert graylog_global_vars.str_indexsets_url == VALID_URL + "/system/indices/index_sets" 
    assert graylog_global_vars.str_node_id_url == VALID_URL + "/system/cluster/node"
    assert graylog_global_vars.str_streams_url == VALID_URL + "/streams"
    assert graylog_global_vars.str_cluster_url == VALID_URL + "/cluster"
    assert graylog_global_vars.str_pth_host_cfg_dir == VALID_CWD + "/host-configs" 
    assert graylog_global_vars.str_pth_host_cfg_template == VALID_CWD + "/host-config-templates" 
    assert graylog_global_vars.str_pth_extrctr_cfg == VALID_CWD + "/extractors" 
    assert graylog_global_vars.str_pth_indices_cfg == VALID_CWD + "/indices" 
    assert graylog_global_vars.str_pth_inputs_cfg == VALID_CWD + "/inputs" 
    assert graylog_global_vars.str_pth_streams_cfg == VALID_CWD + "/streams" 
    assert graylog_global_vars.str_pth_schemas == VALID_CWD + "/schemas"
    assert graylog_global_vars.str_pth_host_schema == VALID_CWD + "/schemas" + "/schema_host.json" 
    assert graylog_global_vars.str_pth_schema_index == VALID_CWD + "/schemas" + "/schema_index.json"  
    assert graylog_global_vars.str_pth_schema_input == VALID_CWD + "/schemas" + "/schema_input.json"
    assert graylog_global_vars.str_pth_schema_extractor == VALID_CWD + "/schemas" + "/schema_extractor.json" 
    assert graylog_global_vars.str_pth_schema_stream == VALID_CWD + "/schemas" + "/schema_stream.json"

def test_set_global_vars_output_4_args(capsys):
    args = [VALID_SCRIPT, VALID_TOKEN, VALID_URL, VERBOSE, VALID_CWD]
    set_global_vars(args)
    captured = capsys.readouterr()
    expected_output = (
        "Assigning global variables.\n"
        "[Done] Assigning global variables.\n\n"
    )
    assert captured.out == expected_output
    assert graylog_global_vars.bool_verbose == False
    assert graylog_global_vars.str_inputs_url == VALID_URL + "/system/inputs"
    assert graylog_global_vars.str_indexsets_url == VALID_URL + "/system/indices/index_sets" 
    assert graylog_global_vars.str_node_id_url == VALID_URL + "/system/cluster/node"
    assert graylog_global_vars.str_streams_url == VALID_URL + "/streams"
    assert graylog_global_vars.str_cluster_url == VALID_URL + "/cluster"
    assert graylog_global_vars.str_pth_host_cfg_dir == VALID_CWD + "/host-configs" 
    assert graylog_global_vars.str_pth_host_cfg_template == VALID_CWD + "/host-config-templates" 
    assert graylog_global_vars.str_pth_extrctr_cfg == VALID_CWD + "/extractors" 
    assert graylog_global_vars.str_pth_indices_cfg == VALID_CWD + "/indices" 
    assert graylog_global_vars.str_pth_inputs_cfg == VALID_CWD + "/inputs" 
    assert graylog_global_vars.str_pth_streams_cfg == VALID_CWD + "/streams" 
    assert graylog_global_vars.str_pth_schemas == VALID_CWD + "/schemas"
    assert graylog_global_vars.str_pth_host_schema == VALID_CWD + "/schemas" + "/schema_host.json" 
    assert graylog_global_vars.str_pth_schema_index == VALID_CWD + "/schemas" + "/schema_index.json"  
    assert graylog_global_vars.str_pth_schema_input == VALID_CWD + "/schemas" + "/schema_input.json"
    assert graylog_global_vars.str_pth_schema_extractor == VALID_CWD + "/schemas" + "/schema_extractor.json" 
    assert graylog_global_vars.str_pth_schema_stream == VALID_CWD + "/schemas" + "/schema_stream.json"