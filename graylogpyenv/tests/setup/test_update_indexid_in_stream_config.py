"""Module:tests.setup.test_update_index_id_in_stream_config_file"""
import os
import requests
import pytest

from src.setup import update_index_id_in_stream_config_file
from tests.common.test_common import create_config_dir
from tests.common.test_common import shared_asserts
from tests.common.test_common import mock_get_response
from tests.common.test_common import create_stream_config_dir
from tests.common.test_common import MOCK_STR_INDEXSETS_URL
from tests.common.test_common import MOCK_DICT_GET_HEADERS
from tests.common.test_common import BOOL_VERBOSE_TRUE

CWD = os.getcwd()
hostconfigdir = CWD + "/tests/test-configs/host-config"
hostconfigfile= CWD + "/tests/test-configs/host-config/samplehost.json"
streamconfigdir = CWD + "/tests/test-configs/streams"
streamconfigfile = CWD + "/tests/test-configs/streams/stream_samplehost.json"

MOCK_GET_INDEXSETID_BYTITLE='{"index_sets": [{ "id": "samplehost_index_setid", "title": "samplehost-stream"}]}'

def test_update_index_id_in_stream_config_file_pass_verbose(mocker,capsys) -> None:
    """Function:test_update_index_id_in_stream_config_file_pass_verbose"""
    mock_response = mock_get_response(200,MOCK_GET_INDEXSETID_BYTITLE)
    mocker.patch('requests.get', return_value=mock_response)
    update_index_id_in_stream_config_file(BOOL_VERBOSE_TRUE, hostconfigfile, streamconfigdir,
        MOCK_STR_INDEXSETS_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    expected_output = "    Updating stream_samplehost.json with index id samplehost_index_setid\n"
    assert captured.out == expected_output

def test_update_index_id_in_stream_config_file_fail_non200(mocker,capsys) -> None:
    """Function:test_update_index_id_in_stream_config_file_fail_non200"""
    mock_response = mock_get_response(404,"Not found")
    mocker.patch('requests.get', return_value=mock_response)
    with pytest.raises(SystemExit) as e:
        update_index_id_in_stream_config_file(BOOL_VERBOSE_TRUE, hostconfigfile, streamconfigdir,
            MOCK_STR_INDEXSETS_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    expected_output = f"[ERROR] Get index id by index name failed. Message:{mock_response.text}\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_update_index_id_in_stream_config_file_fail_update_stream_config(tmp_path, mocker,capsys) -> None:
    """Function:test_update_index_id_in_stream_config_file_fail_update_stream_config"""
    streamconfig=create_stream_config_dir("index_set_id_bad",tmp_path,"config-2")
    streampath = tmp_path.as_posix()+"/config-2/stream_samplehost.json"
    mock_response = mock_get_response(200,MOCK_GET_INDEXSETID_BYTITLE)
    mocker.patch('requests.get', return_value=mock_response)
    with pytest.raises(SystemExit) as e:
        update_index_id_in_stream_config_file(BOOL_VERBOSE_TRUE, hostconfigfile, streamconfig,
            MOCK_STR_INDEXSETS_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    expected_output = f"[ERROR] Couldn't update stream config file {streampath}\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_update_index_id_in_stream_config_file_fail_filenotfound(capsys) -> None:
    """Function:test_update_index_id_in_stream_config_file_fail_filenotfound"""
    with pytest.raises(SystemExit) as e:
        update_index_id_in_stream_config_file(BOOL_VERBOSE_TRUE, "bad_path", streamconfigdir,
            MOCK_STR_INDEXSETS_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    message = "[ERROR] File or directory not found in update_index_id_in_stream_config_file:"
    expected_output = f"{message} [Errno 2] No such file or directory: 'bad_path'\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_update_index_id_in_stream_config_file_fail_requestexception(mocker,capsys) -> None:
    """Function:test_update_index_id_in_stream_config_file_fail_requestexception"""
    mocker.patch('requests.get', side_effect=requests.exceptions.RequestException("Connection error"))
    with pytest.raises(SystemExit) as e:
        update_index_id_in_stream_config_file(BOOL_VERBOSE_TRUE, hostconfigfile, streamconfigdir,
            MOCK_STR_INDEXSETS_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    expected_output = "[ERROR] Request error in update_index_id_in_stream_config_file: Connection error\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_update_index_id_in_stream_config_file_fail_jsondecode(tmp_path,capsys) -> None:
    """Function:test_update_index_id_in_stream_config_file_fail_jsondecode"""
    create_config_dir(tmp_path,"config-1")
    hostconfigfile_path = tmp_path.as_posix()+"/config-1/config_0.json"
    with pytest.raises(SystemExit) as e:
        update_index_id_in_stream_config_file(BOOL_VERBOSE_TRUE, hostconfigfile_path, streamconfigdir,
            MOCK_STR_INDEXSETS_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    message = "[ERROR] There was a problem decoding json in update_index_id_in_stream_config_file:"
    expected_output = f"{message} Expecting value: line 1 column 1 (char 0)\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
