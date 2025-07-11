"""Module:tests.setup.test_create_inputs"""
import os
import requests
import pytest

from src.setup import create_inputs

from tests.common.test_common import create_config_dir
from tests.common.test_common import mock_get_response
from tests.common.test_common import shared_asserts
from tests.common.test_common import BOOL_VERBOSE_TRUE
from tests.common.test_common import MOCK_STR_INPUTS_URL
from tests.common.test_common import MOCK_STR_NODE_URL
from tests.common.test_common import MOCK_DICT_POST_HEADERS
from tests.common.test_common import MOCK_DICT_GET_HEADERS

CWD = os.getcwd()
INPUTCONFIGDIR = CWD + "/tests/test-configs/inputs"
INPUTCONFIGFILE = CWD + "/tests/test-configs/inputs/input_samplehost.json"

def test_create_inputs_verbose_success(mocker,capsys) -> None:
    """Function:test_create_inputs_verbose_success"""
    config_file_list=[INPUTCONFIGFILE]
    mocker.patch("src.setup.get_list_config_files",return_value=config_file_list)
    mocker.patch("src.setup.update_nodeid_in_input_config_files",return_value=None)
    mocker.patch("src.setup.gen_list_inputs_to_create",return_value=config_file_list)
    mocker.patch('json.loads', return_value={"node": "node_id_string", "global": True, "title": "samplehost-input"})
    mocker.patch('src.setup.jq', return_value=["samplehost-input"])
    mock_response = mock_get_response(201,{"id":"new_created_input_id"})
    mocker.patch('requests.post', return_value=mock_response)
    mocker.patch('json.loads', return_value={"id":"new_created_input_id"})
    create_inputs(BOOL_VERBOSE_TRUE,INPUTCONFIGDIR,MOCK_STR_NODE_URL,
        MOCK_STR_INPUTS_URL,MOCK_DICT_GET_HEADERS,MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing inputs\n"
        "    InputTitle: samplehost-input InputID: new_created_input_id Created.\n"
        "[Done] Processing inputs.\n\n"
    )
    assert captured.out == expected_output

def test_create_inputs_fail_post_response(mocker,capsys) -> None:
    """Function:test_create_inputs_fail_post_response"""
    config_file_list=[INPUTCONFIGFILE]
    mocker.patch("src.setup.get_list_config_files",return_value=config_file_list)
    mocker.patch("src.setup.update_nodeid_in_input_config_files",return_value=None)
    mocker.patch("src.setup.gen_list_inputs_to_create",return_value=config_file_list)
    mocker.patch('json.loads', return_value={"node": "node_id_string", "global": True, "title": "samplehost-input"})
    mocker.patch('src.setup.jq', return_value=["samplehost-input"])
    mock_response = mock_get_response(404,"Create input failure")
    mocker.patch('requests.post', return_value=mock_response)
    with pytest.raises(SystemExit) as e:
        create_inputs(BOOL_VERBOSE_TRUE,INPUTCONFIGDIR,MOCK_STR_NODE_URL,
            MOCK_STR_INPUTS_URL,MOCK_DICT_GET_HEADERS,MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing inputs\n"
        "[ERROR] Create input failed. Message: Create input failure\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_create_inputs_fail_file_not_found(mocker,capsys) -> None:
    """Function:test_create_inputs_fail_file_not_found"""
    config_file_list=["bad_path"]
    mocker.patch("src.setup.get_list_config_files",return_value=config_file_list)
    mocker.patch("src.setup.update_nodeid_in_input_config_files",return_value=None)
    mocker.patch("src.setup.gen_list_inputs_to_create",return_value=config_file_list)
    with pytest.raises(SystemExit) as e:
        create_inputs(BOOL_VERBOSE_TRUE,INPUTCONFIGDIR,MOCK_STR_NODE_URL,
            MOCK_STR_INPUTS_URL,MOCK_DICT_GET_HEADERS,MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    message = "[ERROR]: File or directory not found in create inputs:"
    expected_output = (
        "Processing inputs\n"
        f"{message} [Errno 2] No such file or directory: '{config_file_list[0]}'\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_create_inputs_fail_json_decode(tmp_path,mocker,capsys) -> None:
    """Function:test_create_inputs_fail_json_decode"""
    config=create_config_dir(tmp_path,"config-1")
    config_file_list=[tmp_path.as_posix()+"/config-1/config_0.json"]
    mocker.patch("src.setup.get_list_config_files",return_value=config_file_list)
    mocker.patch("src.setup.update_nodeid_in_input_config_files",return_value=None)
    mocker.patch("src.setup.gen_list_inputs_to_create",return_value=config_file_list)
    with pytest.raises(SystemExit) as e:
        create_inputs(BOOL_VERBOSE_TRUE,config,MOCK_STR_NODE_URL,MOCK_STR_INPUTS_URL,
            MOCK_DICT_GET_HEADERS,MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    message = "[ERROR] There was a problem decoding json in create inputs:"
    expected_output = (
        "Processing inputs\n"
        f"{message} Expecting value: line 1 column 1 (char 0)\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_create_inputs_fail_request_exception(mocker,capsys) -> None:
    """Function:test_create_inputs_fail_request_exception"""
    config_file_list=[INPUTCONFIGFILE]
    mocker.patch("src.setup.get_list_config_files",return_value=config_file_list)
    mocker.patch("src.setup.update_nodeid_in_input_config_files",return_value=None)
    mocker.patch("src.setup.gen_list_inputs_to_create",return_value=config_file_list)
    mocker.patch('json.loads', return_value={"node": "node_id_string", "global": True, "title": "samplehost-input"})
    mocker.patch('src.setup.jq', return_value=["input_title_2"])
    mocker.patch('requests.post', side_effect=requests.exceptions.RequestException("Connection error"))
    with pytest.raises(SystemExit) as e:
        create_inputs(BOOL_VERBOSE_TRUE,INPUTCONFIGDIR,MOCK_STR_NODE_URL,
            MOCK_STR_INPUTS_URL,MOCK_DICT_GET_HEADERS,MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing inputs\n"
        "[ERROR] Request error in create inputs: Connection error\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
