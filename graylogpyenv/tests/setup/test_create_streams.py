"""Module:tests.setup.test_create_streams"""
import os
import json
from pathlib import Path
import requests
import pytest

from src.setup import create_streams
from tests.common.test_common import mock_get_response
from tests.common.test_common import shared_asserts
from tests.common.test_common import BOOL_VERBOSE_TRUE
from tests.common.test_common import MOCK_DICT_POST_HEADERS
from tests.common.test_common import MOCK_DICT_GET_HEADERS
from tests.common.test_common import MOCK_STR_INDEXSETS_URL
from tests.common.test_common import MOCK_STR_STREAMS_URL

MOCK_STREAMS_API = '{"stream_id": "new_stream_id"}'
MOCK_GET_INDEXSETID_BYTITLE='{"index_sets": [{ "id": "samplehost_index_setid", "title": "samplehost-stream"}]}'
CWD = os.getcwd()
HOSTCONFIGDIR = CWD + "/tests/test-configs/host-config"
HOSTCONFIGFILE= CWD + "/tests/test-configs/host-config/samplehost.json"
STREAMCONFIGDIR = CWD + "/tests/test-configs/streams"

def create_bad_2_sample_stream_config_dir(base_dir: Path, name: str) -> Path:
    """Function:create_bad_2_sample_stream_config_dir"""
    config_dir = base_dir / name
    config_dir.mkdir()
    file_path = config_dir / "config_0.json"
    input_json_content = {
        "index_set_id_bad": "samplehost_index_setid",
        "title": "samplehost-stream",
    }
    file_path.write_text(json.dumps(input_json_content,indent=2))
    file_path = config_dir / "config_1.json"
    input_content = "bad_content"
    file_path.write_text(input_content)
    return config_dir

def test_create_streams_verbose_success(mocker,capsys) -> None:
    """Function:test_create_streams_verbose_success"""
    mocker.patch("src.setup.gen_list_host_config_files",return_value=[HOSTCONFIGFILE])
    mock_response = mock_get_response(200,MOCK_GET_INDEXSETID_BYTITLE)
    mocker.patch('requests.get', return_value=mock_response)
    mocker.patch("src.setup.gen_list_streams_to_create",return_value=[['samplehost-stream', 'stream_samplehost.json']])
    mock_create_response = mock_get_response(201,MOCK_STREAMS_API)
    mocker.patch('requests.post', return_value=mock_create_response)
    mocker.patch('src.setup.start_stream', return_value="")
    create_streams(BOOL_VERBOSE_TRUE,STREAMCONFIGDIR, HOSTCONFIGDIR, MOCK_STR_INDEXSETS_URL,
        MOCK_STR_STREAMS_URL, MOCK_DICT_GET_HEADERS, MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing streams\n"
        " 1 Stream configs to process.\n"
        "    Updating stream_samplehost.json with index id samplehost_index_setid\n"
        "      Create Stream samplehost-stream from config stream_samplehost.json\n"
        "[Done] Processing streams.\n\n"
    )
    assert captured.out == expected_output

def test_create_streams_verbose_failed(mocker,capsys) -> None:
    """Function:test_create_streams_verbose_failed"""
    mocker.patch("src.setup.gen_list_host_config_files",return_value=[HOSTCONFIGFILE])
    mock_response = mock_get_response(200,MOCK_GET_INDEXSETID_BYTITLE)
    mocker.patch('requests.get', return_value=mock_response)
    mocker.patch("src.setup.gen_list_streams_to_create",return_value=[['samplehost-stream', 'stream_samplehost.json']])
    mock_create_response = mock_get_response(400,"Fail create stream")
    mocker.patch('requests.post', return_value=mock_create_response)
    with pytest.raises(SystemExit) as e:
        create_streams(BOOL_VERBOSE_TRUE,STREAMCONFIGDIR, HOSTCONFIGDIR, MOCK_STR_INDEXSETS_URL,
            MOCK_STR_STREAMS_URL, MOCK_DICT_GET_HEADERS, MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing streams\n"
        " 1 Stream configs to process.\n"
        "    Updating stream_samplehost.json with index id samplehost_index_setid\n"
        "      Create Stream samplehost-stream from config stream_samplehost.json\n"
        f"[ERROR] Create streams failed. Message: {mock_create_response.text}\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_create_streams_fail_filenotfound(capsys) -> None:
    """Function:test_create_streams_fail_filenotfound"""
    with pytest.raises(SystemExit) as e:
        create_streams(BOOL_VERBOSE_TRUE,"bad_path", HOSTCONFIGDIR, MOCK_STR_INDEXSETS_URL,
            MOCK_STR_STREAMS_URL, MOCK_DICT_GET_HEADERS, MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    message = "[ERROR] File or directory not found in create_streams:"
    expected_output = (
        "Processing streams\n"
        f"{message} [Errno 2] No such file or directory: 'bad_path'\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_create_streams_fail_requestexception(mocker,capsys) -> None:
    """Function:test_create_streams_fail_requestexception"""
    mocker.patch("src.setup.gen_list_host_config_files",return_value=[HOSTCONFIGFILE])
    mock_response = mock_get_response(200,MOCK_GET_INDEXSETID_BYTITLE)
    mocker.patch('requests.get', return_value=mock_response)
    mocker.patch("src.setup.gen_list_streams_to_create",return_value=[['samplehost-stream', 'stream_samplehost.json']])
    mocker.patch('requests.post', side_effect=requests.exceptions.RequestException("Connection error"))
    with pytest.raises(SystemExit) as e:
        create_streams(BOOL_VERBOSE_TRUE,STREAMCONFIGDIR, HOSTCONFIGDIR, MOCK_STR_INDEXSETS_URL,
            MOCK_STR_STREAMS_URL, MOCK_DICT_GET_HEADERS, MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing streams\n"
        " 1 Stream configs to process.\n"
        "    Updating stream_samplehost.json with index id samplehost_index_setid\n"
        "      Create Stream samplehost-stream from config stream_samplehost.json\n"
        "[ERROR] Request error in create_streams: Connection error\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_create_streams_fail_jsondecode(tmp_path,mocker,capsys) -> None:
    """Function:test_create_streams_fail_jsondecode"""
    streamconfigdir=create_bad_2_sample_stream_config_dir(tmp_path,"config-2")
    mocker.patch("src.setup.gen_list_host_config_files",return_value=[HOSTCONFIGFILE])
    mocker.patch("src.setup.update_index_id_in_stream_config_file",return_value=None)
    mock_response = mock_get_response(200,MOCK_GET_INDEXSETID_BYTITLE)
    mocker.patch('requests.get', return_value=mock_response)
    mocker.patch("src.setup.gen_list_streams_to_create",return_value=[['samplehost_stream', 'config_1.json']])
    with pytest.raises(SystemExit) as e:
        create_streams(BOOL_VERBOSE_TRUE,streamconfigdir, HOSTCONFIGDIR, MOCK_STR_INDEXSETS_URL,
            MOCK_STR_STREAMS_URL, MOCK_DICT_GET_HEADERS, MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    message = "[ERROR] There was a problem decoding json in create_streams:"
    expected_output = (
        "Processing streams\n"
        " 2 Stream configs to process.\n"
        "      Create Stream samplehost_stream from config config_1.json\n"
        f"{message} Expecting value: line 1 column 1 (char 0)\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
