"""tests.setup test_setup_update_nodeid_in_config_files module"""
from unittest.mock import Mock
import requests
import pytest

from src.setup import update_nodeid_in_input_config_files
from tests.common.test_common import create_sample_input_config_dir
from tests.common.test_common import shared_asserts

MOCK_NODE_URL="https://mock.api/nodeidurl"
MOCK_DICT_GET_HEADERS={"Authorization": "Bearer mock"}
MOCK_JQ_RETURN = {"cluster_id": "string_cluster_id", "node_id": "new_string_node_id",
    "transport_address": "http://mock.api/api/","last_seen": "string_timestamp",
    "short_node_id": "string_short_id", "hostname": "server", "is_leader": True, "is_master": True}
MOCK_VERBOSE = True

def test_update_nodeid_in_input_config_files_pass_verbose(mocker,tmp_path,capsys) -> None:
    """src.setup.test_update_nodeid_in_input_config_files_pass_verbose function"""
    config = create_sample_input_config_dir(tmp_path, "configA")
    list_configs = [config.as_posix()+ "/config_0.json"]
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = MOCK_JQ_RETURN
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_response)
    mocker.patch('json.loads', return_value=MOCK_JQ_RETURN)
    mocker.patch('src.setup.jq', return_value=["new_string_node_id"])
    mocker.patch('json.loads', return_value={"node": "node_id_string", "global": True, "title": "input_title"})
    update_nodeid_in_input_config_files(MOCK_VERBOSE,list_configs,MOCK_NODE_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    path_2_file = tmp_path / "configA" / "config_0.json"
    assert path_2_file.read_text() == '{\n  "node": "new_string_node_id",\n  "global": true,\n  "title": "input_title"\n}'
    expected_output = (
        "  Replace nodeid: new_string_node_id in input config files.\n"
        f"    Updating node id in:{path_2_file}\n"
    )
    assert captured.out == expected_output

def test_update_nodeid_in_input_config_files_fail_getnodeid(mocker,capsys) -> None:
    """src.setup.test_update_nodeid_in_input_config_files_fail_getnodeid function"""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = {"Bad response"}
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_response)
    with pytest.raises(SystemExit) as e:
        update_nodeid_in_input_config_files(MOCK_VERBOSE,["some_config_dir"],MOCK_NODE_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "[ERROR] API call to: https://mock.api/nodeidurl Failed. Message: {'Bad response'}\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_update_nodeid_in_input_config_files_fail_file_update(mocker,tmp_path,capsys) -> None:
    """src.setup.test_update_nodeid_in_input_config_files_fail_file_update function"""
    config = create_sample_input_config_dir(tmp_path, "configA")
    list_configs = [config.as_posix()+ "/config_0.json"]
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = MOCK_JQ_RETURN
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_response)
    mocker.patch('json.loads', return_value=MOCK_JQ_RETURN)
    mocker.patch('src.setup.jq', return_value=["new_string_node_id"])
    mocker.patch('json.loads', return_value={"missing_node": "node_id_string"})
    with pytest.raises(SystemExit) as e:
        update_nodeid_in_input_config_files(MOCK_VERBOSE,list_configs,MOCK_NODE_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    path_2_file = tmp_path / "configA" / "config_0.json"
    expected_output = (
        "  Replace nodeid: new_string_node_id in input config files.\n"
        f"    Updating node id in:{path_2_file}\n"
        f"[ERROR] Couldn't update config file {path_2_file} with new_string_node_id\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_update_nodeid_in_input_config_files_fail_file_notfound(mocker,capsys) -> None:
    """src.setup.test_update_nodeid_in_input_config_files_fail_file_notfound function"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = MOCK_JQ_RETURN
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_response)
    mocker.patch('json.loads', return_value=MOCK_JQ_RETURN)
    mocker.patch('src.setup.jq', return_value=["new_string_node_id"])
    with pytest.raises(SystemExit) as e:
        update_nodeid_in_input_config_files(MOCK_VERBOSE,["bad_path"],MOCK_NODE_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    message = "[ERROR]: File or directory not found in update_nodeid_in_input_config_files:"
    expected_output = (
        "  Replace nodeid: new_string_node_id in input config files.\n"
        "    Updating node id in:bad_path\n"
        f"{message} [Errno 2] No such file or directory: 'bad_path'\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_update_nodeid_in_input_config_files_fail_json_decode(mocker,capsys) -> None:
    """src.setup.test_update_nodeid_in_input_config_files_fail_json_decode function"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "Bad json response"
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_response)
    with pytest.raises(SystemExit) as e:
        update_nodeid_in_input_config_files(MOCK_VERBOSE,["bad_path"],MOCK_NODE_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    message = "[ERROR] There was a problem decoding json in update_nodeid_in_input_config_files:"
    expected_output = (
        f"{message} Expecting value: line 1 column 1 (char 0)\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_update_nodeid_in_input_config_files_fail_requests(mocker,capsys) -> None:
    """src.setup.test_update_nodeid_in_input_config_files_fail_requests function"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "Bad json response"
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', side_effect=requests.exceptions.RequestException("Connection error"))
    with pytest.raises(SystemExit) as e:
        update_nodeid_in_input_config_files(MOCK_VERBOSE,["bad_path"],MOCK_NODE_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "[ERROR] Request error in update_nodeid_in_input_config_files: Connection error\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
