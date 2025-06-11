"""tests.setup test_gen_list_streams_to_create module"""
from unittest.mock import Mock
import requests
import pytest

from src.setup import gen_list_streams_to_create

from tests.common.test_common import create_sample_host_config_dir
from tests.setup.test_setup_common import create_bad_config_dir
from tests.common.test_common import shared_asserts

MOCK_DICT_GET_HEADERS={"Authorization": "Bearer mock"}
MOCK_BOOL_VERBOSE=True
MOCK_STREAMS_URL="https://mock.api/streams"
MOCK_STREAMS_API= '{"streams": [{ "id": "stream_id", "title": "existing_stream" }]}'
MOCK_STREAMS_API_EXIST= '{"streams": [{ "id": "stream_id", "title": "samplehost_stream" }]}'

def test_gen_list_streams_to_create_pass(tmp_path, mocker) -> None:
    """tests.setup.test_gen_list_streams_to_create_pass function"""
    create_sample_host_config_dir(tmp_path,"config-1")
    hostconfigfile_path = tmp_path.as_posix()+"/config-1/config_0.json"
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = MOCK_STREAMS_API
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_response)
    returnval = gen_list_streams_to_create(MOCK_BOOL_VERBOSE, [hostconfigfile_path],
        MOCK_STREAMS_URL, MOCK_DICT_GET_HEADERS)
    assert returnval == [['samplehost_stream', 'config_0.json']]

def test_gen_list_streams_to_create_fail_filenotfound(tmp_path,capsys) -> None:
    """tests.setup.test_gen_list_streams_to_create_fail_filenotfound function"""
    create_sample_host_config_dir(tmp_path,"config-1")
    hostconfigfile_path = tmp_path.as_posix()+"/config-1/config_not_exist.json"
    with pytest.raises(SystemExit) as e:
        gen_list_streams_to_create(MOCK_BOOL_VERBOSE, [hostconfigfile_path],
        MOCK_STREAMS_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    message = "[ERROR] File or directory not found in gen_list_streams_to_create:"
    expected_output = f"{message} [Errno 2] No such file or directory: '{hostconfigfile_path}'\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_gen_list_streams_to_create_fail_non200(tmp_path, mocker, capsys) -> None:
    """tests.setup.test_gen_list_streams_to_create_fail_non200 function"""
    create_sample_host_config_dir(tmp_path,"config-1")
    hostconfigfile_path = tmp_path.as_posix()+"/config-1/config_0.json"
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "bad response"
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_response)
    with pytest.raises(SystemExit) as e:
        gen_list_streams_to_create(MOCK_BOOL_VERBOSE, [hostconfigfile_path],
        MOCK_STREAMS_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    expected_output = "[ERROR] Get streams failed. Message: bad response\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_gen_list_streams_to_create_pass_existing(tmp_path, mocker,capsys) -> None:
    """tests.setup.test_gen_list_streams_to_create_pass function"""
    create_sample_host_config_dir(tmp_path,"config-1")
    hostconfigfile_path = tmp_path.as_posix()+"/config-1/config_0.json"
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = MOCK_STREAMS_API_EXIST
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_response)
    returnval = gen_list_streams_to_create(MOCK_BOOL_VERBOSE, [hostconfigfile_path],
        MOCK_STREAMS_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    expected_output = "      Stream samplehost_stream Already exists, won't create.\n"
    assert captured.out == expected_output
    assert not returnval

def test_gen_list_streams_to_create_fail_requestexception(tmp_path, mocker,capsys) -> None:
    """tests.setup.test_gen_list_streams_to_create_fail_requestexception function"""
    create_sample_host_config_dir(tmp_path,"config-1")
    hostconfigfile_path = tmp_path.as_posix()+"/config-1/config_0.json"
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "Bad response"
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', side_effect=requests.exceptions.RequestException("Connection error"))
    with pytest.raises(SystemExit) as e:
        gen_list_streams_to_create(MOCK_BOOL_VERBOSE, [hostconfigfile_path],
        MOCK_STREAMS_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    expected_output = "[ERROR] Request error in gen_list_streams_to_create: Connection error\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_gen_list_streams_to_create_fail_jsondecode(tmp_path,capsys) -> None:
    """tests.setup.test_gen_list_streams_to_create_fail_jsondecode function"""
    create_bad_config_dir(tmp_path,"config-1")
    hostconfigfile_path = tmp_path.as_posix()+"/config-1/config_0.json"
    with pytest.raises(SystemExit) as e:
        gen_list_streams_to_create(MOCK_BOOL_VERBOSE, [hostconfigfile_path],
        MOCK_STREAMS_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    message = "[ERROR] There was a problem decoding json in gen_list_streams_to_create:"
    expected_output = f"{message} Expecting value: line 1 column 1 (char 0)\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
