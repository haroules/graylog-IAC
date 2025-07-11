"""Module:tests.setup.test_update_nodeid_in_config_files"""
import os
from pathlib import Path
import json
import requests
import pytest

from src.setup import update_nodeid_in_input_config_files
from tests.common.test_common import shared_asserts
from tests.common.test_common import mock_get_response
from tests.common.test_common import MOCK_STR_NODE_URL
from tests.common.test_common import MOCK_DICT_GET_HEADERS
from tests.common.test_common import BOOL_VERBOSE_TRUE

MOCK_JQ_RETURN = {"cluster_id": "string_cluster_id", "node_id": "new_string_node_id",
    "transport_address": "http://mock.api/api/","last_seen": "string_timestamp",
    "short_node_id": "string_short_id", "hostname": "server", "is_leader": True, "is_master": True}

CWD = os.getcwd()
INPUTCONFIGFILE = CWD + "/tests/test-configs/inputs/input_samplehost.json"

def create_sample_input_config_dir(base_dir: Path, name: str) -> Path:
    """Function:create_sample_input_config_dir"""
    config_dir = base_dir / name
    config_dir.mkdir()
    file_path = config_dir / "config_0.json"
    input_json_content = ({"node": "node_id_string", "global": True, "title": "input_title_2"})
    file_path.write_text(json.dumps(input_json_content,indent=2))
    return config_dir

def test_update_nodeid_in_input_config_files_pass_verbose(mocker,tmp_path,capsys) -> None:
    """Function:test_update_nodeid_in_input_config_files_pass_verbose"""
    # have to use tmp filesystem as it will overwrite config file
    config = create_sample_input_config_dir(tmp_path, "configA")
    list_configs = [config.as_posix()+ "/config_0.json"]
    mock_response = mock_get_response(200,MOCK_JQ_RETURN)
    mocker.patch('requests.get', return_value=mock_response)
    mocker.patch('json.loads', return_value=MOCK_JQ_RETURN)
    mocker.patch('src.setup.jq', return_value=["new_string_node_id"])
    mocker.patch('json.loads', return_value={"node": "node_id_string", "global": True, "title": "input_title"})
    update_nodeid_in_input_config_files(BOOL_VERBOSE_TRUE,list_configs,MOCK_STR_NODE_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    path_2_file = tmp_path / "configA" / "config_0.json"
    assert path_2_file.read_text() == '{\n  "node": "new_string_node_id",\n  "global": true,\n  "title": "input_title"\n}'
    expected_output = (
        "  Replace nodeid: new_string_node_id in input config files.\n"
        f"    Updating node id in:{path_2_file}\n"
    )
    assert captured.out == expected_output

def test_update_nodeid_in_input_config_files_fail_getnodeid(mocker,capsys) -> None:
    """Function:test_update_nodeid_in_input_config_files_fail_getnodeid"""
    mock_response = mock_get_response(404,{"Bad response"})
    mocker.patch('requests.get', return_value=mock_response)
    with pytest.raises(SystemExit) as e:
        update_nodeid_in_input_config_files(BOOL_VERBOSE_TRUE,["some_config_dir"],MOCK_STR_NODE_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        f"[ERROR] API call to: {MOCK_STR_NODE_URL} Failed. Message: " + "{'Bad response'}\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_update_nodeid_in_input_config_files_fail_file_update(mocker,capsys) -> None:
    """Function:test_update_nodeid_in_input_config_files_fail_file_update"""
    list_configs = [INPUTCONFIGFILE]
    mock_response = mock_get_response(200,MOCK_JQ_RETURN)
    mocker.patch('requests.get', return_value=mock_response)
    mocker.patch('json.loads', return_value=MOCK_JQ_RETURN)
    mocker.patch('src.setup.jq', return_value=["new_string_node_id"])
    mocker.patch('json.loads', return_value={"missing_node": "node_id_string"})
    with pytest.raises(SystemExit) as e:
        update_nodeid_in_input_config_files(BOOL_VERBOSE_TRUE,list_configs,MOCK_STR_NODE_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "  Replace nodeid: new_string_node_id in input config files.\n"
        f"    Updating node id in:{INPUTCONFIGFILE}\n"
        f"[ERROR] Couldn't update config file {INPUTCONFIGFILE} with new_string_node_id\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_update_nodeid_in_input_config_files_fail_file_notfound(mocker,capsys) -> None:
    """Function:test_update_nodeid_in_input_config_files_fail_file_notfound"""
    mock_response = mock_get_response(200,MOCK_JQ_RETURN)
    mocker.patch('requests.get', return_value=mock_response)
    mocker.patch('json.loads', return_value=MOCK_JQ_RETURN)
    mocker.patch('src.setup.jq', return_value=["new_string_node_id"])
    with pytest.raises(SystemExit) as e:
        update_nodeid_in_input_config_files(BOOL_VERBOSE_TRUE,["bad_path"],MOCK_STR_NODE_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    message = "[ERROR]: File or directory not found in update_nodeid_in_input_config_files:"
    expected_output = (
        "  Replace nodeid: new_string_node_id in input config files.\n"
        "    Updating node id in:bad_path\n"
        f"{message} [Errno 2] No such file or directory: 'bad_path'\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_update_nodeid_in_input_config_files_fail_json_decode(mocker,capsys) -> None:
    """Function:test_update_nodeid_in_input_config_files_fail_json_decode"""
    mock_response = mock_get_response(200,"Bad json response")
    mocker.patch('requests.get', return_value=mock_response)
    with pytest.raises(SystemExit) as e:
        update_nodeid_in_input_config_files(BOOL_VERBOSE_TRUE,["bad_path"],MOCK_STR_NODE_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    message = "[ERROR] There was a problem decoding json in update_nodeid_in_input_config_files:"
    expected_output = (
        f"{message} Expecting value: line 1 column 1 (char 0)\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_update_nodeid_in_input_config_files_fail_requests(mocker,capsys) -> None:
    """Function:test_update_nodeid_in_input_config_files_fail_requests function"""
    mocker.patch('requests.get', side_effect=requests.exceptions.RequestException("Connection error"))
    with pytest.raises(SystemExit) as e:
        update_nodeid_in_input_config_files(BOOL_VERBOSE_TRUE,["bad_path"],MOCK_STR_NODE_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "[ERROR] Request error in update_nodeid_in_input_config_files: Connection error\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
