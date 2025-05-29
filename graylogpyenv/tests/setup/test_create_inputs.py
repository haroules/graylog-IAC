"""tests.setup test_create_inputs module"""
from unittest.mock import Mock
import requests
import pytest

from src.setup import create_inputs
from tests.setup.test_setup_common import create_sample_input_config_dir
from tests.setup.test_setup_common import create_bad_sample_input_config_dir

MOCK_INPUTS_URL="https://mock.api/inputs"
MOCK_NODE_URL="https://mock.api/nodeidurl"
MOCK_DICT_POST_HEADERS={"Authorization": "Bearer mock"}
MOCK_DICT_GET_HEADERS={"Authorization": "Bearer mock"}
MOCK_BOOL_VEBOSE=True


def test_create_inputs_verbose_success(tmp_path,mocker,capsys) -> None:
    """setup test_create_inputs_non_exist_verbose_success function"""
    config=create_sample_input_config_dir(tmp_path,"config-1")
    config_file_list=[tmp_path.as_posix()+"/config-1/config_0.json"]
    mocker.patch("src.setup.get_list_config_files",return_value=config_file_list)
    mocker.patch("src.setup.update_nodeid_in_input_config_files",return_value=None)
    mocker.patch("src.setup.gen_list_inputs_to_create",return_value=config_file_list)
    mocker.patch('json.loads', return_value={"node": "node_id_string", "global": True, "title": "input_title_2"})
    mocker.patch('src.setup.jq', return_value=["input_title_2"])
    mock_response = Mock()
    mock_response.status_code = 201
    mock_response.text = {"id":"new_created_input_id"}
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.post', return_value=mock_response)
    mocker.patch('json.loads', return_value={"id":"new_created_input_id"})
    create_inputs(MOCK_BOOL_VEBOSE,config,MOCK_NODE_URL,MOCK_INPUTS_URL,MOCK_DICT_GET_HEADERS,MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing inputs\n"
        "    InputTitle: input_title_2 InputID: new_created_input_id Created.\n"
        "[Done] Processing inputs.\n\n"
    )
    assert captured.out == expected_output

def test_create_inputs_fail_post_response(tmp_path,mocker,capsys) -> None:
    """setup test_create_inputs_fail_post_response function"""
    config=create_sample_input_config_dir(tmp_path,"config-1")
    config_file_list=[tmp_path.as_posix()+"/config-1/config_0.json"]
    mocker.patch("src.setup.get_list_config_files",return_value=config_file_list)
    mocker.patch("src.setup.update_nodeid_in_input_config_files",return_value=None)
    mocker.patch("src.setup.gen_list_inputs_to_create",return_value=config_file_list)
    mocker.patch('json.loads', return_value={"node": "node_id_string", "global": True, "title": "input_title_2"})
    mocker.patch('src.setup.jq', return_value=["input_title_2"])
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "Create input failure"
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.post', return_value=mock_response)
    with pytest.raises(SystemExit) as e:
        create_inputs(MOCK_BOOL_VEBOSE,config,MOCK_NODE_URL,MOCK_INPUTS_URL,MOCK_DICT_GET_HEADERS,MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing inputs\n"
        "[ERROR] Create input failed. Message: Create input failure\n"
    )
    assert captured.out == expected_output
    assert e.value.code == 1

def test_create_inputs_fail_file_not_found(tmp_path,mocker,capsys) -> None:
    """setup test_create_inputs_non_exist_fail_file_not_found"""
    config=create_sample_input_config_dir(tmp_path,"config-1")
    config_file_list=[tmp_path.as_posix()+"/config-1/config_3.json"]
    mocker.patch("src.setup.get_list_config_files",return_value=config_file_list)
    mocker.patch("src.setup.update_nodeid_in_input_config_files",return_value=None)
    mocker.patch("src.setup.gen_list_inputs_to_create",return_value=config_file_list)
    with pytest.raises(SystemExit) as e:
        create_inputs(MOCK_BOOL_VEBOSE,config,MOCK_NODE_URL,MOCK_INPUTS_URL,MOCK_DICT_GET_HEADERS,MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    message = "[ERROR]: File or directory not found in create inputs:"
    expected_output = (
        "Processing inputs\n"
        f"{message} [Errno 2] No such file or directory: '{config_file_list[0]}'\n"
    )
    assert captured.out == expected_output
    assert e.value.code == 1

def test_create_inputs_fail_json_decode(tmp_path,mocker,capsys) -> None:
    """setup test_create_inputs_fail_json_decode function"""
    config=create_bad_sample_input_config_dir(tmp_path,"config-1")
    config_file_list=[tmp_path.as_posix()+"/config-1/config_0.json"]
    mocker.patch("src.setup.get_list_config_files",return_value=config_file_list)
    mocker.patch("src.setup.update_nodeid_in_input_config_files",return_value=None)
    mocker.patch("src.setup.gen_list_inputs_to_create",return_value=config_file_list)
    with pytest.raises(SystemExit) as e:
        create_inputs(MOCK_BOOL_VEBOSE,config,MOCK_NODE_URL,MOCK_INPUTS_URL,MOCK_DICT_GET_HEADERS,MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    message = "[ERROR] There was a problem decoding json in create inputs:"
    expected_output = (
        "Processing inputs\n"
        f"{message} Expecting value: line 1 column 1 (char 0)\n"
    )
    assert captured.out == expected_output
    assert e.value.code == 1

def test_create_inputs_fail_request_exception(tmp_path,mocker,capsys) -> None:
    """setup test_create_inputs_fail_request_exception function"""
    config=create_sample_input_config_dir(tmp_path,"config-1")
    config_file_list=[tmp_path.as_posix()+"/config-1/config_0.json"]
    mocker.patch("src.setup.get_list_config_files",return_value=config_file_list)
    mocker.patch("src.setup.update_nodeid_in_input_config_files",return_value=None)
    mocker.patch("src.setup.gen_list_inputs_to_create",return_value=config_file_list)
    mocker.patch('json.loads', return_value={"node": "node_id_string", "global": True, "title": "input_title_2"})
    mocker.patch('src.setup.jq', return_value=["input_title_2"])
    mocker.patch('requests.post', side_effect=requests.exceptions.RequestException("Connection error"))
    with pytest.raises(SystemExit) as e:
        create_inputs(MOCK_BOOL_VEBOSE,config,MOCK_NODE_URL,MOCK_INPUTS_URL,MOCK_DICT_GET_HEADERS,MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing inputs\n"
        "[ERROR] Request error in create inputs: Connection error\n"
    )
    assert captured.out == expected_output
    assert e.value.code == 1
