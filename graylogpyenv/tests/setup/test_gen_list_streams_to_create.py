"""Module:tests.setup.test_gen_list_streams_to_create"""
import os
import requests
import pytest

from src.setup import gen_list_streams_to_create
from tests.common.test_common import create_config_dir
from tests.common.test_common import shared_asserts
from tests.common.test_common import mock_get_response
from tests.common.test_common import MOCK_DICT_GET_HEADERS
from tests.common.test_common import BOOL_VERBOSE_TRUE
from tests.common.test_common import MOCK_STR_STREAMS_URL

MOCK_STREAMS_API= '{"streams": [{ "id": "stream_id", "title": "existing_stream" }]}'
MOCK_STREAMS_API_EXIST= '{"streams": [{ "id": "stream_id", "title": "samplehost-stream" }]}'

CWD = os.getcwd()
HOSTCONFIGFILE= CWD + "/tests/test-configs/host-config/samplehost.json"

def test_gen_list_streams_to_create_pass(mocker) -> None:
    """Function:test_gen_list_streams_to_create_pass"""
    mock_response = mock_get_response(200,MOCK_STREAMS_API)
    mocker.patch('requests.get', return_value=mock_response)
    returnval = gen_list_streams_to_create(BOOL_VERBOSE_TRUE, [HOSTCONFIGFILE],
        MOCK_STR_STREAMS_URL, MOCK_DICT_GET_HEADERS)
    assert returnval == [['samplehost-stream', 'stream_samplehost.json']]

def test_gen_list_streams_to_create_fail_filenotfound(capsys) -> None:
    """Function:test_gen_list_streams_to_create_fail_filenotfound"""
    with pytest.raises(SystemExit) as e:
        gen_list_streams_to_create(BOOL_VERBOSE_TRUE, ['bad_path'],
        MOCK_STR_STREAMS_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    message = "[ERROR] File or directory not found in gen_list_streams_to_create:"
    expected_output = f"{message} [Errno 2] No such file or directory: 'bad_path'\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_gen_list_streams_to_create_fail_non200(mocker, capsys) -> None:
    """Function:test_gen_list_streams_to_create_fail_non200"""
    mock_response = mock_get_response(404,"bad response")
    mocker.patch('requests.get', return_value=mock_response)
    with pytest.raises(SystemExit) as e:
        gen_list_streams_to_create(BOOL_VERBOSE_TRUE, [HOSTCONFIGFILE],
        MOCK_STR_STREAMS_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    expected_output = "[ERROR] Get streams failed. Message: bad response\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_gen_list_streams_to_create_pass_existing(mocker,capsys) -> None:
    """Function:test_gen_list_streams_to_create_pass"""
    mock_response = mock_get_response(200,MOCK_STREAMS_API_EXIST)
    mocker.patch('requests.get', return_value=mock_response)
    returnval = gen_list_streams_to_create(BOOL_VERBOSE_TRUE, [HOSTCONFIGFILE],
        MOCK_STR_STREAMS_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    expected_output = "      Stream samplehost-stream Already exists, won't create.\n"
    assert captured.out == expected_output
    assert not returnval

def test_gen_list_streams_to_create_fail_requestexception(mocker,capsys) -> None:
    """Function:test_gen_list_streams_to_create_fail_requestexception"""
    mocker.patch('requests.get', side_effect=requests.exceptions.RequestException("Connection error"))
    with pytest.raises(SystemExit) as e:
        gen_list_streams_to_create(BOOL_VERBOSE_TRUE, [HOSTCONFIGFILE],
        MOCK_STR_STREAMS_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    expected_output = "[ERROR] Request error in gen_list_streams_to_create: Connection error\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_gen_list_streams_to_create_fail_jsondecode(tmp_path,capsys) -> None:
    """Function:test_gen_list_streams_to_create_fail_jsondecode"""
    create_config_dir(tmp_path,"config-1")
    hostconfigfile_path = tmp_path.as_posix()+"/config-1/config_0.json"
    with pytest.raises(SystemExit) as e:
        gen_list_streams_to_create(BOOL_VERBOSE_TRUE, [hostconfigfile_path],
        MOCK_STR_STREAMS_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    message = "[ERROR] There was a problem decoding json in gen_list_streams_to_create:"
    expected_output = f"{message} Expecting value: line 1 column 1 (char 0)\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
