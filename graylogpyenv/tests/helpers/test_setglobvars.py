"""Module:tests.helpers.test_setglobalvars"""
import os
import global_vars

from src.helpers import set_global_vars
from src.helpers import set_global_vars_verify
from tests.common.test_common import MOCK_TEST_URL
from tests.common.test_common import BOOL_VERBOSE_FALSE
from tests.common.test_common import MOCK_TOKEN
from tests.common.test_common import MOCK_SCRIPT

VALID_SCRIPT_VERIFY = "graylog_verify.py"
VALID_CWD = os.path.dirname(os.getcwd())

def check_exist_isdir(path) -> None:
    """Function:check_exist_isdir"""
    assert os.path.exists(path)
    assert os.path.isdir(path)

def check_exist_isfile(path) -> None:
    """Function:check_exist_isfile"""
    assert os.path.exists(path)
    assert os.path.isfile(path)

def validate_url_sets(valid_url :str) -> None:
    """Function:validate_url_sets"""
    assert global_vars.STR_INPUTS_URL == valid_url + "/system/inputs"
    assert global_vars.STR_INDEXSETS_URL == valid_url + "/system/indices/index_sets"
    assert global_vars.STR_NODE_ID_URL == valid_url + "/system/cluster/node"
    assert global_vars.STR_STREAMS_URL == valid_url + "/streams"
    assert global_vars.STR_CLUSTER_URL == valid_url + "/cluster"

def validate_path_sets(valid_cwd :str) -> None:
    """Function:validate_path_sets"""
    assert global_vars.STR_PTH_HOST_CFG_DIR == valid_cwd + "/host-configs"
    check_exist_isdir(global_vars.STR_PTH_HOST_CFG_DIR)
    assert global_vars.STR_PTH_HOST_CFG_TEMPLATE == valid_cwd + "/host-config-templates"
    check_exist_isdir(global_vars.STR_PTH_HOST_CFG_TEMPLATE)
    assert global_vars.STR_PTH_EXTRCTR_CFG == valid_cwd + "/extractors"
    check_exist_isdir(global_vars.STR_PTH_EXTRCTR_CFG)
    assert global_vars.STR_PTH_INDICES_CFG == valid_cwd + "/indices"
    check_exist_isdir(global_vars.STR_PTH_INDICES_CFG)
    assert global_vars.STR_PTH_INPUTS_CFG == valid_cwd + "/inputs"
    check_exist_isdir(global_vars.STR_PTH_INPUTS_CFG)
    assert global_vars.STR_PTH_STREAMS_CFG == valid_cwd + "/streams"
    check_exist_isdir(global_vars.STR_PTH_STREAMS_CFG)
    assert global_vars.STR_PTH_SCHEMAS == valid_cwd + "/schemas"
    check_exist_isdir(global_vars.STR_PTH_SCHEMAS)
    assert global_vars.STR_PTH_HOST_SCHEMA == valid_cwd + "/schemas" + "/host.json"
    check_exist_isfile(global_vars.STR_PTH_HOST_SCHEMA)
    assert global_vars.STR_PTH_SCHEMA_INDEX == valid_cwd + "/schemas" + "/index.json"
    check_exist_isfile(global_vars.STR_PTH_SCHEMA_INDEX)
    assert global_vars.STR_PTH_SCHEMA_INPUT == valid_cwd + "/schemas" + "/input.json"
    check_exist_isfile(global_vars.STR_PTH_SCHEMA_INPUT)
    assert global_vars.STR_PTH_SCHEMA_EXTRACTOR == valid_cwd + "/schemas" + "/extractor.json"
    check_exist_isfile(global_vars.STR_PTH_SCHEMA_EXTRACTOR)
    assert global_vars.STR_PTH_SCHEMA_STREAM == valid_cwd + "/schemas" + "/stream.json"
    check_exist_isfile(global_vars.STR_PTH_SCHEMA_STREAM)

def test_set_global_vars_output_3_args(capsys) -> None:
    """Function:test_set_global_vars_output_3_args"""
    args = [MOCK_SCRIPT, MOCK_TOKEN, MOCK_TEST_URL, VALID_CWD]
    set_global_vars(args)
    captured = capsys.readouterr()
    expected_output = (
        "Assigning global variables.\n"
        "[Done] Assigning global variables.\n\n"
    )
    validate_url_sets(MOCK_TEST_URL)
    validate_path_sets(VALID_CWD)
    assert captured.out == expected_output
    assert global_vars.BOOL_VERBOSE is True
    assert global_vars.LIST_BUILTIN_INDEX_NAMES == ["Default index set","Graylog Events","Graylog System Events"]
    assert global_vars.LIST_BUILTIN_STREAMS_IDS == ["000000000000000000000001","000000000000000000000002", \
                                                    "000000000000000000000003"]

def test_set_global_vars_output_4_args(capsys) -> None:
    """Function:test_set_global_vars_output_4_args"""
    args = [MOCK_SCRIPT, MOCK_TOKEN, MOCK_TEST_URL, BOOL_VERBOSE_FALSE, VALID_CWD]
    set_global_vars(args)
    captured = capsys.readouterr()
    expected_output = (
        "Assigning global variables.\n"
        "[Done] Assigning global variables.\n\n"
    )
    assert captured.out == expected_output
    assert global_vars.BOOL_VERBOSE is False
    validate_url_sets(MOCK_TEST_URL)
    validate_path_sets(VALID_CWD)

def test_set_global_vars_verify_output_1_arg(capsys) -> None:
    """Function:test_set_global_vars_verify_output_1_arg"""
    args = [VALID_SCRIPT_VERIFY,VALID_CWD]
    set_global_vars_verify(args)
    captured = capsys.readouterr()
    expected_output = (
        "Assigning global variables.\n"
        "[Done] Assigning global variables.\n\n"
    )
    assert captured.out == expected_output
    assert global_vars.BOOL_VERBOSE is True
    validate_path_sets(VALID_CWD)

def test_set_global_vars_verify_output_2_args(capsys) -> None:
    """Function:test_set_global_vars_verify_output_2_args"""
    args = [VALID_SCRIPT_VERIFY, BOOL_VERBOSE_FALSE, VALID_CWD]
    set_global_vars_verify(args)
    captured = capsys.readouterr()
    expected_output = (
        "Assigning global variables.\n"
        "[Done] Assigning global variables.\n\n"
    )
    assert captured.out == expected_output
    assert global_vars.BOOL_VERBOSE is False
    validate_path_sets(VALID_CWD)
