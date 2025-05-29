"""tests.setup test_create_streams module"""
from unittest.mock import Mock
import requests
import pytest

from src.setup import create_streams
from tests.setup.test_setup_common import create_sample_host_config_dir
from tests.setup.test_setup_common import create_sample_stream_config_dir
from tests.setup.test_setup_common import create_bad_2_sample_stream_config_dir
MOCK_STREAMS_URL="https://mock.api/streams"
MOCK_INDEXSETS_URL="https://mock.api/indexsets"
MOCK_DICT_POST_HEADERS={"Authorization": "Bearer mock"}
MOCK_DICT_GET_HEADERS={"Authorization": "Bearer mock"}
MOCK_BOOL_VEBOSE=True
MOCK_STREAMS_API = '{"stream_id": "new_stream_id"}'
MOCK_GET_INDEXSETID_BYTITLE='{"index_sets": [{ "id": "samplehost_index_setid", "title": "samplehost-stream"}]}'

def test_create_streams_verbose_success(tmp_path,mocker,capsys) -> None:
    """setup test_create_streams_verbose_success function"""
    hostconfigdir=create_sample_host_config_dir(tmp_path,"config-1")
    hostconfigfile_path = tmp_path.as_posix()+"/config-1/config_0.json"
    streamconfigdir=create_sample_stream_config_dir(tmp_path,"config-2")
    mocker.patch("src.setup.gen_list_host_config_files",return_value=[hostconfigfile_path])
    mock_indexid_response = Mock()
    mock_indexid_response.status_code = 200
    mock_indexid_response.text = MOCK_GET_INDEXSETID_BYTITLE
    mock_indexid_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_indexid_response)
    mocker.patch("src.setup.gen_list_streams_to_create",return_value=[['samplehost_stream', 'config_0.json']])
    mock_create_response = Mock()
    mock_create_response.status_code = 201
    mock_create_response.text = MOCK_STREAMS_API
    mock_create_response.raise_for_status = Mock()
    mocker.patch('requests.post', return_value=mock_create_response)
    mocker.patch('src.setup.start_stream', return_value="")
    create_streams(MOCK_BOOL_VEBOSE,streamconfigdir, hostconfigdir, MOCK_INDEXSETS_URL,
        MOCK_STREAMS_URL, MOCK_DICT_GET_HEADERS, MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing streams\n"
        " 1 Stream configs to process.\n"
        "    Updating config_0.json with index id samplehost_index_setid\n"
        "      Create Stream samplehost_stream from config config_0.json\n"
        "[Done] Processing streams.\n\n"
    )
    assert captured.out == expected_output

def test_create_streams_verbose_failed(tmp_path,mocker,capsys) -> None:
    """setup test_create_streams_verbose_failed function"""
    hostconfigdir=create_sample_host_config_dir(tmp_path,"config-1")
    hostconfigfile_path = tmp_path.as_posix()+"/config-1/config_0.json"
    streamconfigdir=create_sample_stream_config_dir(tmp_path,"config-2")
    mocker.patch("src.setup.gen_list_host_config_files",return_value=[hostconfigfile_path])
    mock_indexid_response = Mock()
    mock_indexid_response.status_code = 200
    mock_indexid_response.text = MOCK_GET_INDEXSETID_BYTITLE
    mock_indexid_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_indexid_response)
    mocker.patch("src.setup.gen_list_streams_to_create",return_value=[['samplehost_stream', 'config_0.json']])
    mock_create_response = Mock()
    mock_create_response.status_code = 400
    mock_create_response.text = "Fail create stream"
    mock_create_response.raise_for_status = Mock()
    mocker.patch('requests.post', return_value=mock_create_response)
    with pytest.raises(SystemExit) as e:
        create_streams(MOCK_BOOL_VEBOSE,streamconfigdir, hostconfigdir, MOCK_INDEXSETS_URL,
            MOCK_STREAMS_URL, MOCK_DICT_GET_HEADERS, MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing streams\n"
        " 1 Stream configs to process.\n"
        "    Updating config_0.json with index id samplehost_index_setid\n"
        "      Create Stream samplehost_stream from config config_0.json\n"
        f"[ERROR] Create streams failed. Message: {mock_create_response.text}\n"
    )
    assert captured.out == expected_output
    assert e.value.code == 1

def test_create_streams_fail_filenotfound(tmp_path,capsys) -> None:
    """setup test_create_streams_fail_filenotfound function"""
    hostconfigdir=create_sample_host_config_dir(tmp_path,"config-1")
    with pytest.raises(SystemExit) as e:
        create_streams(MOCK_BOOL_VEBOSE,"bad_path", hostconfigdir, MOCK_INDEXSETS_URL,
            MOCK_STREAMS_URL, MOCK_DICT_GET_HEADERS, MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    message = "[ERROR] File or directory not found in create_streams:"
    expected_output = (
        "Processing streams\n"
        f"{message} [Errno 2] No such file or directory: 'bad_path'\n"
    )
    assert captured.out == expected_output
    assert e.value.code == 1

def test_create_streams_fail_requestexception(tmp_path,mocker,capsys) -> None:
    """setup test_create_streams_fail_requestexception function"""
    hostconfigdir=create_sample_host_config_dir(tmp_path,"config-1")
    hostconfigfile_path = tmp_path.as_posix()+"/config-1/config_0.json"
    streamconfigdir=create_sample_stream_config_dir(tmp_path,"config-2")
    mocker.patch("src.setup.gen_list_host_config_files",return_value=[hostconfigfile_path])
    mock_indexid_response = Mock()
    mock_indexid_response.status_code = 200
    mock_indexid_response.text = MOCK_GET_INDEXSETID_BYTITLE
    mock_indexid_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_indexid_response)
    mocker.patch("src.setup.gen_list_streams_to_create",return_value=[['samplehost_stream', 'config_0.json']])
    mocker.patch('requests.post', side_effect=requests.exceptions.RequestException("Connection error"))
    with pytest.raises(SystemExit) as e:
        create_streams(MOCK_BOOL_VEBOSE,streamconfigdir, hostconfigdir, MOCK_INDEXSETS_URL,
            MOCK_STREAMS_URL, MOCK_DICT_GET_HEADERS, MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing streams\n"
        " 1 Stream configs to process.\n"
        "    Updating config_0.json with index id samplehost_index_setid\n"
        "      Create Stream samplehost_stream from config config_0.json\n"
        "[ERROR] Request error in create_streams: Connection error\n"
    )
    assert captured.out == expected_output
    assert e.value.code == 1

def test_create_streams_fail_jsondecode(tmp_path,mocker,capsys) -> None:
    """setup test_create_streams_fail_jsondecode function"""
    hostconfigdir=create_sample_host_config_dir(tmp_path,"config-1")
    hostconfigfile_path = tmp_path.as_posix()+"/config-1/config_0.json"
    streamconfigdir=create_bad_2_sample_stream_config_dir(tmp_path,"config-2")
    mocker.patch("src.setup.gen_list_host_config_files",return_value=[hostconfigfile_path])
    mocker.patch("src.setup.update_index_id_in_stream_config_file",return_value=None)
    mock_indexid_response = Mock()
    mock_indexid_response.status_code = 200
    mock_indexid_response.text = MOCK_GET_INDEXSETID_BYTITLE
    mock_indexid_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_indexid_response)
    mocker.patch("src.setup.gen_list_streams_to_create",return_value=[['samplehost_stream', 'config_1.json']])
    with pytest.raises(SystemExit) as e:
        create_streams(MOCK_BOOL_VEBOSE,streamconfigdir, hostconfigdir, MOCK_INDEXSETS_URL,
            MOCK_STREAMS_URL, MOCK_DICT_GET_HEADERS, MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    message = "[ERROR] There was a problem decoding json in create_streams:"
    expected_output = (
        "Processing streams\n"
        " 2 Stream configs to process.\n"
        "      Create Stream samplehost_stream from config config_1.json\n"
        f"{message} Expecting value: line 1 column 1 (char 0)\n"
    )
    assert captured.out == expected_output
    assert e.value.code == 1
