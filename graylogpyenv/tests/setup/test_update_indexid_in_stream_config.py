"""tests.setup test_update_index_id_in_stream_config_file module"""
from unittest.mock import Mock
import requests
import pytest

from src.setup import update_index_id_in_stream_config_file
from tests.common.test_common import create_sample_stream_config_dir
from tests.common.test_common import create_sample_host_config_dir
from tests.setup.test_setup_common import create_bad_sample_stream_config_dir
from tests.setup.test_setup_common import create_bad_config_dir
from tests.common.test_common import shared_asserts

MOCK_INDEX_URL="https://mock.api/indexsets"
MOCK_DICT_GET_HEADERS={"Authorization": "Bearer mock"}
MOCK_BOOL_VERBOSE=True
MOCK_GET_INDEXSETID_BYTITLE='{"index_sets": [{ "id": "samplehost_index_setid", "title": "samplehost-stream"}]}'

def test_update_index_id_in_stream_config_file_pass_verbose(tmp_path, mocker,capsys) -> None:
    """tests.setup.test_update_index_id_in_stream_config_file_pass_verbose function"""
    create_sample_host_config_dir(tmp_path,"config-1")
    hostconfigfile_path = tmp_path.as_posix()+"/config-1/config_0.json"
    streamconfig=create_sample_stream_config_dir(tmp_path,"config-2")
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = MOCK_GET_INDEXSETID_BYTITLE
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_response)
    update_index_id_in_stream_config_file(MOCK_BOOL_VERBOSE, hostconfigfile_path, streamconfig,
        MOCK_INDEX_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    expected_output = "    Updating config_0.json with index id samplehost_index_setid\n"
    assert captured.out == expected_output

def test_update_index_id_in_stream_config_file_fail_non200(tmp_path, mocker,capsys) -> None:
    """tests.setup.test_update_index_id_in_stream_config_file_fail_non200 function"""
    create_sample_host_config_dir(tmp_path,"config-1")
    hostconfigfile_path = tmp_path.as_posix()+"/config-1/config_0.json"
    streamconfig=create_sample_stream_config_dir(tmp_path,"config-2")
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "Not found"
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_response)
    with pytest.raises(SystemExit) as e:
        update_index_id_in_stream_config_file(MOCK_BOOL_VERBOSE, hostconfigfile_path, streamconfig,
            MOCK_INDEX_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    expected_output = f"[ERROR] Get index id by index name failed. Message:{mock_response.text}\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_update_index_id_in_stream_config_file_fail_update_stream_config(tmp_path, mocker,capsys) -> None:
    """tests.setup.test_update_index_id_in_stream_config_file_fail_update_stream_config function"""
    create_sample_host_config_dir(tmp_path,"config-1")
    hostconfigfile_path = tmp_path.as_posix()+"/config-1/config_0.json"
    streamconfig=create_bad_sample_stream_config_dir(tmp_path,"config-2")
    streampath = tmp_path.as_posix()+"/config-2/config_0.json"
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = MOCK_GET_INDEXSETID_BYTITLE
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_response)
    with pytest.raises(SystemExit) as e:
        update_index_id_in_stream_config_file(MOCK_BOOL_VERBOSE, hostconfigfile_path, streamconfig,
            MOCK_INDEX_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    expected_output = f"[ERROR] Couldn't update stream config file {streampath}\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_update_index_id_in_stream_config_file_fail_filenotfound(tmp_path,capsys) -> None:
    """tests.setup.test_update_index_id_in_stream_config_file_fail_filenotfound function"""
    streamconfig=create_bad_config_dir(tmp_path,"config-2")
    with pytest.raises(SystemExit) as e:
        update_index_id_in_stream_config_file(MOCK_BOOL_VERBOSE, "bad_path", streamconfig,
            MOCK_INDEX_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    message = "[ERROR] File or directory not found in update_index_id_in_stream_config_file:"
    expected_output = f"{message} [Errno 2] No such file or directory: 'bad_path'\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_update_index_id_in_stream_config_file_fail_requestexception(tmp_path, mocker,capsys) -> None:
    """tests.setup.test_update_index_id_in_stream_config_file_fail_requestexception function"""
    create_sample_host_config_dir(tmp_path,"config-1")
    hostconfigfile_path = tmp_path.as_posix()+"/config-1/config_0.json"
    streamconfig=create_sample_stream_config_dir(tmp_path,"config-2")
    mock_response = Mock()
    mock_response.status_code = ""
    mock_response.text = "Not found"
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', side_effect=requests.exceptions.RequestException("Connection error"))
    with pytest.raises(SystemExit) as e:
        update_index_id_in_stream_config_file(MOCK_BOOL_VERBOSE, hostconfigfile_path, streamconfig,
            MOCK_INDEX_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    expected_output = "[ERROR] Request error in update_index_id_in_stream_config_file: Connection error\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_update_index_id_in_stream_config_file_fail_jsondecode(tmp_path,capsys) -> None:
    """tests.setup.test_update_index_id_in_stream_config_file_fail_jsondecode function"""
    create_bad_config_dir(tmp_path,"config-1")
    hostconfigfile_path = tmp_path.as_posix()+"/config-1/config_0.json"
    streamconfig=create_bad_config_dir(tmp_path,"config-2")
    with pytest.raises(SystemExit) as e:
        update_index_id_in_stream_config_file(MOCK_BOOL_VERBOSE, hostconfigfile_path, streamconfig,
            MOCK_INDEX_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    message = "[ERROR] There was a problem decoding json in update_index_id_in_stream_config_file:"
    expected_output = f"{message} Expecting value: line 1 column 1 (char 0)\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
