"""tests.clean test_remove_streams module"""
from unittest import mock
from unittest.mock import Mock
import requests
import pytest

from src.clean import remove_streams
from tests.common.test_common import shared_asserts

MOCK_BOOL_VERBOSE = True
MOCK_STR_STREAMS_URL = "http://test-url.com/streams"
MOCK_DICT_GET_HEADERS = {"Authorization": "Bearer token"}
MOCK_DICT_POST_HEADERS = {"Authorization": "Bearer token"}
MOCK_BUILTIN_STREAMS_IDS = ["0001", "0002", "0003"]
MOCK_LIST_ALL_STREAM_IDS = ["0001", "0002", "0003", "0004"]
MOCK_LIST_STREAM_IDS_TO_DELETE = ["0004"]
MOCK_LIST_STREAM_NAMES_TO_DELETE = ["stream4"]
MOCK_REMOVE_STREAMS_ARGS = [MOCK_BOOL_VERBOSE, MOCK_STR_STREAMS_URL, MOCK_DICT_GET_HEADERS,
    MOCK_DICT_POST_HEADERS, MOCK_BUILTIN_STREAMS_IDS]

@pytest.fixture(name="mocked_patches")
def mocked_dependencies():
    """tests.clean.mocked_dependencies function"""
    with mock.patch('src.clean.get_list_stream_names_to_delete') as mock_list_stream_names_to_delete, \
        mock.patch('src.clean.get_clean_list_ids_to_delete') as mock_list_stream_ids_to_delete, \
        mock.patch('src.clean.get_list_all_stream_ids') as mock_list_all_stream_ids:
        yield mock_list_stream_names_to_delete, mock_list_stream_ids_to_delete, mock_list_all_stream_ids

def test_remove_streams_pass_removables( mocked_patches, mocker, capsys) -> None:
    """tests.clean.test_remove_streams_pass_removables function"""
    mock_get_list_stream_names_to_delete, mock_get_clean_list_stream_ids_to_delete, \
    mock_get_list_all_stream_ids = mocked_patches
    mock_get_list_all_stream_ids.return_value = MOCK_LIST_ALL_STREAM_IDS
    mock_get_clean_list_stream_ids_to_delete.return_value = MOCK_LIST_STREAM_IDS_TO_DELETE
    mock_get_list_stream_names_to_delete.return_value = MOCK_LIST_STREAM_NAMES_TO_DELETE
    mock_response = Mock()
    mock_response.status_code = 204
    mock_response.text = ''
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.delete', return_value=mock_response)
    result = remove_streams(*MOCK_REMOVE_STREAMS_ARGS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing streams for deletion\n"
        f"{len(MOCK_LIST_STREAM_IDS_TO_DELETE)} Streams found\n"
        f"Removing Stream Ids {MOCK_LIST_STREAM_IDS_TO_DELETE}\n"
        f"Removing Stream Titles {MOCK_LIST_STREAM_NAMES_TO_DELETE}\n"
        "[Done] processing streams for deletion.\n\n"
    )
    assert captured.out == expected_output
    assert result is True
    mock_get_list_all_stream_ids.assert_called_once()
    mock_get_clean_list_stream_ids_to_delete.assert_called_once()
    mock_get_list_stream_names_to_delete.assert_called_once()

def test_remove_streams_pass_noremovable( mocker, capsys) -> None:
    """tests.clean.test_remove_streams_pass_noremovable function"""
    mock_response = Mock()
    mock_response.status_code = 204
    mock_response.text = ''
    mock_response.raise_for_status = Mock()
    mocker.patch('src.clean.get_list_all_stream_ids', return_value=[])
    result = remove_streams(*MOCK_REMOVE_STREAMS_ARGS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing streams for deletion\n"
        "No streams to delete.\n"
        "[Done] processing streams for deletion.\n\n"
    )
    assert captured.out == expected_output
    assert result is True

def test_remove_streams_fail_to_delete(mocked_patches, mocker, capsys) -> None:
    """tests.clean.test_remove_streams_fail_to_delete function"""
    mock_get_list_stream_names_to_delete, mock_get_clean_list_stream_ids_to_delete, \
        mock_get_list_all_stream_ids = mocked_patches
    mock_get_list_all_stream_ids.return_value = MOCK_LIST_ALL_STREAM_IDS
    mock_get_clean_list_stream_ids_to_delete.return_value = MOCK_LIST_STREAM_IDS_TO_DELETE
    mock_get_list_stream_names_to_delete.return_value = MOCK_LIST_STREAM_NAMES_TO_DELETE
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = ''
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.delete', return_value=mock_response)
    with pytest.raises(SystemExit) as e:
        remove_streams(*MOCK_REMOVE_STREAMS_ARGS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing streams for deletion\n"
        f"{len(MOCK_LIST_STREAM_IDS_TO_DELETE)} Streams found\n"
        f"Removing Stream Ids {MOCK_LIST_STREAM_IDS_TO_DELETE}\n"
        f"Removing Stream Titles {MOCK_LIST_STREAM_NAMES_TO_DELETE}\n"
        f"[ERROR] Failed to delete stream: {MOCK_LIST_STREAM_IDS_TO_DELETE[0]}\n\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
    mock_get_list_all_stream_ids.assert_called_once()
    mock_get_clean_list_stream_ids_to_delete.assert_called_once()
    mock_get_list_stream_names_to_delete.assert_called_once()

def test_remove_streams_fail_request_exception(mocked_patches, mocker, capsys) -> None:
    """tests.clean.test_remove_streams_fail_request_exception function"""
    mock_get_list_stream_names_to_delete, mock_get_clean_list_stream_ids_to_delete, \
        mock_get_list_all_stream_ids = mocked_patches
    mock_get_list_all_stream_ids.return_value = MOCK_LIST_ALL_STREAM_IDS
    mock_get_clean_list_stream_ids_to_delete.return_value = MOCK_LIST_STREAM_IDS_TO_DELETE
    mock_get_list_stream_names_to_delete.return_value = MOCK_LIST_STREAM_NAMES_TO_DELETE
    mocker.patch('requests.delete', side_effect=requests.exceptions.RequestException("Connection error"))
    with pytest.raises(SystemExit) as e:
        remove_streams(*MOCK_REMOVE_STREAMS_ARGS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing streams for deletion\n"
        f"{len(MOCK_LIST_STREAM_IDS_TO_DELETE)} Streams found\n"
        f"Removing Stream Ids {MOCK_LIST_STREAM_IDS_TO_DELETE}\n"
        f"Removing Stream Titles {MOCK_LIST_STREAM_NAMES_TO_DELETE}\n"
        "[ERROR] Request error in remove streams: Connection error\n\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
    mock_get_list_all_stream_ids.assert_called_once()
    mock_get_clean_list_stream_ids_to_delete.assert_called_once()
    mock_get_list_stream_names_to_delete.assert_called_once()

def test_remove_streams_fail_json_decode_error(mocked_patches, mocker, capsys) -> None:
    """tests.clean.test_remove_streams_fail_json_decode_error function"""
    mock_get_list_stream_names_to_delete, mock_get_clean_list_stream_ids_to_delete, \
        mock_get_list_all_stream_ids = mocked_patches
    mock_get_list_all_stream_ids.return_value = MOCK_LIST_ALL_STREAM_IDS
    mock_get_clean_list_stream_ids_to_delete.return_value = MOCK_LIST_STREAM_IDS_TO_DELETE
    mock_get_list_stream_names_to_delete.return_value = MOCK_LIST_STREAM_NAMES_TO_DELETE
    mocker.patch('requests.delete', side_effect=ValueError("Decoding error"))
    with pytest.raises(SystemExit) as e:
        remove_streams(*MOCK_REMOVE_STREAMS_ARGS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing streams for deletion\n"
        f"{len(MOCK_LIST_STREAM_IDS_TO_DELETE)} Streams found\n"
        f"Removing Stream Ids {MOCK_LIST_STREAM_IDS_TO_DELETE}\n"
        f"Removing Stream Titles {MOCK_LIST_STREAM_NAMES_TO_DELETE}\n"
        "[ERROR] JSON decoding error in remove streams: Decoding error\n\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
    mock_get_list_all_stream_ids.assert_called_once()
    mock_get_clean_list_stream_ids_to_delete.assert_called_once()
    mock_get_list_stream_names_to_delete.assert_called_once()
