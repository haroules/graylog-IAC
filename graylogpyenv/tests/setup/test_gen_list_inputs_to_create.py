"""Module:tests.setup.test_gen_list_inputs_to_create"""
import os
import pytest

from src.setup import gen_list_inputs_to_create
from tests.common.test_common import create_config_dir
from tests.common.test_common import shared_asserts
from tests.common.test_common import MOCK_STR_INPUTS_URL
from tests.common.test_common import MOCK_DICT_GET_HEADERS
from tests.common.test_common import BOOL_VERBOSE_TRUE

CWD = os.getcwd()
INPUTCONFIGFLE = CWD + "/tests/test-configs/inputs/input_samplehost.json"

MOCK_API_RETURN = {"inputs": [ { "title": "input_title_1", "global": True, "name": "input_name_1" } ] }
MOCK_JSON_FILE = {"node": "node_id_string", "global": True, "title": "input_title_2"}

def test_gen_list_inputs_to_create_pass(mocker) -> None:
    """Function:test_gen_list_inputs_to_create_pass_verbose"""
    list_configs=[INPUTCONFIGFLE]
    mocker.patch('src.setup.gen_list_inputs_titles', return_value=["input_title_1"])
    mocker.patch('json.loads', return_value = [MOCK_JSON_FILE ])
    mocker.patch('src.setup.jq', return_value = ["input_title_2"])
    mocker.patch('src.helpers.contains_sublist', return_value=False)
    return_val = gen_list_inputs_to_create(BOOL_VERBOSE_TRUE,list_configs,MOCK_STR_INPUTS_URL,MOCK_DICT_GET_HEADERS)
    assert return_val == list_configs

def test_gen_list_inputs_to_create_pass_existing_verbose(mocker,capsys) -> None:
    """Function:test_gen_list_inputs_to_create_pass_existing_verbose"""
    list_configs=[INPUTCONFIGFLE]
    mocker.patch('src.setup.gen_list_inputs_titles', return_value=["input_title_1"])
    mocker.patch('json.loads', return_value = [MOCK_JSON_FILE ])
    mocker.patch('src.setup.jq', return_value = ["input_title_1"])
    mocker.patch('src.helpers.contains_sublist', return_value=False)
    return_val = gen_list_inputs_to_create(BOOL_VERBOSE_TRUE,list_configs,MOCK_STR_INPUTS_URL,MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    expected_output = "    input_title_1 Input already exists, skipping creation\n"
    assert captured.out == expected_output
    assert not return_val

def test_gen_list_inputs_to_create_fail_filenotfound(mocker,capsys) -> None:
    """Function:test_gen_list_inputs_to_create_fail_filenotfound"""
    mocker.patch('src.setup.gen_list_inputs_titles', return_value=["input_title_1"])
    with pytest.raises(SystemExit) as e:
        gen_list_inputs_to_create(BOOL_VERBOSE_TRUE,["bad_path"],MOCK_STR_INPUTS_URL,MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    message = "[ERROR]: File or directory not found in gen_list_inputs_to_create:"
    expected_output = f"{message} [Errno 2] No such file or directory: 'bad_path'\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_gen_list_inputs_to_create_fail_json_decode(mocker,tmp_path,capsys) -> None:
    """Function:test_gen_list_inputs_to_create_fail_json_decode"""
    config = create_config_dir(tmp_path, "configA")
    list_configs = [config.as_posix()+ "/config_0.json"]
    mocker.patch('src.setup.gen_list_inputs_titles', return_value=["input_title_1"])
    with pytest.raises(SystemExit) as e:
        gen_list_inputs_to_create(BOOL_VERBOSE_TRUE,list_configs,MOCK_STR_INPUTS_URL,MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    message = "[ERROR] There was a problem decoding json in gen_list_inputs_to_create:"
    expected_output = f"{message} Expecting value: line 1 column 1 (char 0)\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
