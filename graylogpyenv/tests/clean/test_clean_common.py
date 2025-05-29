"""clean test_index_sets_ids_common module"""
from unittest.mock import Mock
import requests

from src.clean import get_clean_list_ids_to_delete
from src.clean import get_list_all_index_sets_ids
from src.clean import get_list_all_builtin_index_set_ids
from src.clean import get_list_all_stream_ids
from src.clean import get_list_stream_names_to_delete

MOCK_LIST_STREAM_IDS = ["00001"]
MOCK_STR_STREAMS_URL = "http://test-url.com/streams"
MOCK_STR_INDEXSETS_URL = "http://test-url.com/index_sets"
MOCK_DICT_GET_HEADERS = {"Authorization": "Bearer token"}

MOCK_LIST_ALL_IDS = ["0001", "0002", "0003", "0004"]
MOCK_BUILTIN_IDS = ["0001", "0002", "0003"]
MOCK_LIST_IDS_TO_DELETE = ["0004"]

def test_get_clean_list_ids_to_delete_pass() -> None:
    """clean test_get_clean_list_ids_to_delete_pass function"""
    result = get_clean_list_ids_to_delete(MOCK_LIST_ALL_IDS, MOCK_BUILTIN_IDS)
    assert result == MOCK_LIST_IDS_TO_DELETE

def test_get_list_all_index_sets_ids_fail_request_exception(mocker) -> None:
    """clean test_get_list_all_index_sets_ids_fail_request_exception function"""
    mocker.patch('requests.get', side_effect=requests.exceptions.RequestException("Connection error"))
    mock_exit = mocker.patch('sys.exit')
    get_list_all_index_sets_ids(MOCK_STR_INDEXSETS_URL, MOCK_DICT_GET_HEADERS)
    mock_exit.assert_called_once_with(1)

def test_get_list_all_builtin_index_set_ids_fail_request_exception(mocker) -> None:
    """clean test_get_list_all_builtin_index_set_ids_fail_request_exception function"""
    mocker.patch('requests.get', side_effect=requests.exceptions.RequestException("Connection error"))
    mock_exit = mocker.patch('sys.exit')
    get_list_all_builtin_index_set_ids(MOCK_STR_INDEXSETS_URL, MOCK_DICT_GET_HEADERS, ["index1"])
    mock_exit.assert_called_once_with(1)

def test_get_list_all_index_sets_ids_fail_json_decode_error(mocker) -> None:
    """clean test_get_list_all_index_sets_ids_fail_json_decode_error function"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = 'invalid json'
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_response)
    mocker.patch('json.loads', side_effect=ValueError("Decoding error"))
    mock_exit = mocker.patch('sys.exit')
    get_list_all_index_sets_ids(MOCK_STR_INDEXSETS_URL, MOCK_DICT_GET_HEADERS)
    mock_exit.assert_called_once_with(1)

def test_get_list_all_builtin_index_set_ids_fail_json_decode_error(mocker) -> None:
    """clean test_get_list_all_builtin_index_set_ids_fail_json_decode_error function"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = 'invalid json'
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_response)
    mocker.patch('json.loads', side_effect=ValueError("Decoding error"))
    mock_exit = mocker.patch('sys.exit')
    get_list_all_builtin_index_set_ids(MOCK_STR_INDEXSETS_URL, MOCK_DICT_GET_HEADERS, ["index1"])
    mock_exit.assert_called_once_with(1)

def test_get_list_stream_names_to_delete_fail_request_exception(mocker,capsys) -> None:
    """clean test_get_list_stream_names_to_delete_fail_request_exception function"""
    mocker.patch('requests.get', side_effect=requests.exceptions.RequestException("Connection error"))
    mock_exit = mocker.patch('sys.exit')
    get_list_stream_names_to_delete(MOCK_LIST_STREAM_IDS, MOCK_STR_STREAMS_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    assert captured.out == "[ERROR] Request error in get_list_stream_names_to_delete: Connection error\n\n"
    mock_exit.assert_called_once_with(1)

def test_get_list_all_stream_ids_fail_request_exception(mocker) -> None:
    """clean test_get_list_all_stream_ids_fail_request_exception function"""
    mocker.patch('requests.get', side_effect=requests.exceptions.RequestException("Connection error"))
    mock_exit = mocker.patch('sys.exit')
    get_list_all_stream_ids(MOCK_STR_STREAMS_URL, MOCK_DICT_GET_HEADERS)
    mock_exit.assert_called_once_with(1)

def test_get_list_stream_names_to_delete_fail_json_decode_error(mocker,capsys) -> None:
    """clean test_get_list_stream_names_to_delete_fail_json_decode_error function"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = 'invalid json'
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_response)
    mocker.patch('json.loads', side_effect=ValueError("Decoding error"))
    mock_exit = mocker.patch('sys.exit')
    get_list_stream_names_to_delete(MOCK_LIST_STREAM_IDS, MOCK_STR_STREAMS_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    assert captured.out == "[ERROR] JSON decoding error in get_list_stream_names_to_delete: Decoding error\n\n"
    mock_exit.assert_called_once_with(1)

def test_get_list_all_stream_ids_fail_json_decode_error(mocker) -> None:
    """clean test_get_list_all_stream_ids_fail_json_decode_error function"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = 'invalid json'
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_response)
    mocker.patch('json.loads', side_effect=ValueError("Decoding error"))
    mock_exit = mocker.patch('sys.exit')
    get_list_all_stream_ids(MOCK_STR_STREAMS_URL, MOCK_DICT_GET_HEADERS)
    mock_exit.assert_called_once_with(1)
