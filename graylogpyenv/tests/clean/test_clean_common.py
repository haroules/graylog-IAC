"""Module:tests.clean.test_clean_common"""
import requests

from src.clean import get_clean_list_ids_to_delete
from src.clean import get_list_all_index_sets_ids
from src.clean import get_list_all_builtin_index_set_ids
from src.clean import get_list_all_stream_ids
from src.clean import get_list_stream_names_to_delete
from tests.common.test_common import mock_get_response
from tests.common.test_common import MOCK_DICT_GET_HEADERS
from tests.common.test_common import MOCK_STR_INDEXSETS_URL
from tests.common.test_common import MOCK_STR_STREAMS_URL

MOCK_LIST_STREAM_IDS = ["00001"]
MOCK_LIST_ALL_IDS = ["0001", "0002", "0003", "0004"]
MOCK_BUILTIN_IDS = ["0001", "0002", "0003"]
MOCK_LIST_IDS_TO_DELETE = ["0004"]

def test_get_clean_list_ids_to_delete_pass() -> None:
    """Function:test_get_clean_list_ids_to_delete_pass"""
    result = get_clean_list_ids_to_delete(MOCK_LIST_ALL_IDS, MOCK_BUILTIN_IDS)
    assert result == MOCK_LIST_IDS_TO_DELETE

def test_get_list_all_index_sets_ids_fail_request_exception(mocker) -> None:
    """Function:test_get_list_all_index_sets_ids_fail_request_exception"""
    mocker.patch('requests.get', side_effect=requests.exceptions.RequestException("Connection error"))
    mock_exit = mocker.patch('sys.exit')
    get_list_all_index_sets_ids(MOCK_STR_INDEXSETS_URL, MOCK_DICT_GET_HEADERS)
    mock_exit.assert_called_once_with(1)

def test_get_list_all_builtin_index_set_ids_fail_request_exception(mocker) -> None:
    """Function:test_get_list_all_builtin_index_set_ids_fail_request_exception"""
    mocker.patch('requests.get', side_effect=requests.exceptions.RequestException("Connection error"))
    mock_exit = mocker.patch('sys.exit')
    get_list_all_builtin_index_set_ids(MOCK_STR_INDEXSETS_URL, MOCK_DICT_GET_HEADERS, ["index1"])
    mock_exit.assert_called_once_with(1)

def test_get_list_all_index_sets_ids_fail_json_decode_error(mocker) -> None:
    """Function:test_get_list_all_index_sets_ids_fail_json_decode_error"""
    mock_response = mock_get_response(200,"invalid json")
    mocker.patch('requests.get', return_value=mock_response)
    mocker.patch('json.loads', side_effect=ValueError("Decoding error"))
    mock_exit = mocker.patch('sys.exit')
    get_list_all_index_sets_ids(MOCK_STR_INDEXSETS_URL, MOCK_DICT_GET_HEADERS)
    mock_exit.assert_called_once_with(1)

def test_get_list_all_builtin_index_set_ids_fail_json_decode_error(mocker) -> None:
    """Function:test_get_list_all_builtin_index_set_ids_fail_json_decode_error"""
    mock_response = mock_get_response(200,"invalid json")
    mocker.patch('requests.get', return_value=mock_response)
    mocker.patch('json.loads', side_effect=ValueError("Decoding error"))
    mock_exit = mocker.patch('sys.exit')
    get_list_all_builtin_index_set_ids(MOCK_STR_INDEXSETS_URL, MOCK_DICT_GET_HEADERS, ["index1"])
    mock_exit.assert_called_once_with(1)

def test_get_list_stream_names_to_delete_fail_request_exception(mocker,capsys) -> None:
    """Function:test_get_list_stream_names_to_delete_fail_request_exception"""
    mocker.patch('requests.get', side_effect=requests.exceptions.RequestException("Connection error"))
    mock_exit = mocker.patch('sys.exit')
    get_list_stream_names_to_delete(MOCK_LIST_STREAM_IDS, MOCK_STR_STREAMS_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    assert captured.out == "[ERROR] Request error in get_list_stream_names_to_delete: Connection error\n\n"
    mock_exit.assert_called_once_with(1)

def test_get_list_all_stream_ids_fail_request_exception(mocker) -> None:
    """Function:test_get_list_all_stream_ids_fail_request_exception"""
    mocker.patch('requests.get', side_effect=requests.exceptions.RequestException("Connection error"))
    mock_exit = mocker.patch('sys.exit')
    get_list_all_stream_ids(MOCK_STR_STREAMS_URL, MOCK_DICT_GET_HEADERS)
    mock_exit.assert_called_once_with(1)

def test_get_list_stream_names_to_delete_fail_json_decode_error(mocker,capsys) -> None:
    """Function:test_get_list_stream_names_to_delete_fail_json_decode_error"""
    mock_response = mock_get_response(200,"invalid json")
    mocker.patch('requests.get', return_value=mock_response)
    mocker.patch('json.loads', side_effect=ValueError("Decoding error"))
    mock_exit = mocker.patch('sys.exit')
    get_list_stream_names_to_delete(MOCK_LIST_STREAM_IDS, MOCK_STR_STREAMS_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    assert captured.out == "[ERROR] JSON decoding error in get_list_stream_names_to_delete: Decoding error\n\n"
    mock_exit.assert_called_once_with(1)

def test_get_list_all_stream_ids_fail_json_decode_error(mocker) -> None:
    """Function:test_get_list_all_stream_ids_fail_json_decode_error"""
    mock_response = mock_get_response(200,"invalid json")
    mocker.patch('requests.get', return_value=mock_response)
    mocker.patch('json.loads', side_effect=ValueError("Decoding error"))
    mock_exit = mocker.patch('sys.exit')
    get_list_all_stream_ids(MOCK_STR_STREAMS_URL, MOCK_DICT_GET_HEADERS)
    mock_exit.assert_called_once_with(1)
