"""clean test_remove_indexsets module"""
from unittest import mock
from unittest.mock import Mock
import requests
import pytest

from src.clean import remove_indexsets

MOCK_BOOL_VERBOSE = True
MOCK_STR_INDEXSETS_URL = "http://test-url.com/index_sets"
MOCK_DICT_GET_HEADERS = {"Authorization": "Bearer token"}
MOCK_DICT_POST_HEADERS = {"Authorization": "Bearer token"}
MOCK_LIST_BUILTIN_INDEX_SET_NAMES = ["index1", "index2", "index3"]
MOCK_LIST_BUILTIN_INDEX_SET_IDS = ["0001", "0002", "0003"]
MOCK_LIST_ALL_INDEX_SETS_IDS = ["0001", "0002", "0003", "0004"]
MOCK_LIST_INDEX_SET_IDS_TO_DELETE = ["0004"]
MOCK_LIST_INDEX_SET_NAMES_TO_DELETE = ["index4"]
MOCK_REMOVE_INDEXSETS_ARGS = [MOCK_BOOL_VERBOSE, MOCK_STR_INDEXSETS_URL, MOCK_DICT_GET_HEADERS,
                MOCK_DICT_POST_HEADERS, MOCK_LIST_BUILTIN_INDEX_SET_NAMES]

@pytest.fixture(name="mocked_patches")
def mocked_dependencies():
    """clean mocked_dependencies function"""
    with mock.patch('src.clean.gen_list_index_set_names_to_delete') as list_index_set_names_to_delete, \
        mock.patch('src.clean.get_clean_list_ids_to_delete') as list_index_set_ids_to_delete, \
        mock.patch('src.clean.get_list_all_builtin_index_set_ids') as list_builtin_index_set_ids, \
        mock.patch('src.clean.get_list_all_index_sets_ids') as list_all_index_sets_ids:
        yield list_index_set_names_to_delete, list_index_set_ids_to_delete, list_builtin_index_set_ids, list_all_index_sets_ids

def test_remove_indexsets_pass_removables(mocked_patches,mocker,capsys) -> None:
    """clean test_remove_indexsets_pass_removables function"""
    mock_gen_list_index_set_names_to_delete, mock_get_list_index_set_ids_to_delete,\
        mock_get_list_builtin_index_set_ids, mock_get_list_all_index_sets_ids = mocked_patches
    mock_get_list_all_index_sets_ids.return_value = MOCK_LIST_ALL_INDEX_SETS_IDS
    mock_get_list_builtin_index_set_ids.return_value = MOCK_LIST_BUILTIN_INDEX_SET_IDS
    mock_get_list_index_set_ids_to_delete.return_value = MOCK_LIST_INDEX_SET_IDS_TO_DELETE
    mock_gen_list_index_set_names_to_delete.return_value = MOCK_LIST_INDEX_SET_NAMES_TO_DELETE
    mock_response = Mock()
    mock_response.status_code = 204
    mock_response.text = ''
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.delete', return_value = mock_response)
    result = remove_indexsets(*MOCK_REMOVE_INDEXSETS_ARGS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing index sets for deletion\n"
        f"{len(MOCK_LIST_INDEX_SET_NAMES_TO_DELETE)} Index Sets found\n"
        f"Removing IndexSet Ids {MOCK_LIST_INDEX_SET_IDS_TO_DELETE}\n"
        f"Removing IndexSet Titles {MOCK_LIST_INDEX_SET_NAMES_TO_DELETE}\n"
        "[Done] processing index sets for deletion.\n\n"
    )
    assert captured.out == expected_output
    assert result is True
    mock_get_list_all_index_sets_ids.assert_called_once()
    mock_get_list_builtin_index_set_ids.assert_called_once()
    mock_gen_list_index_set_names_to_delete.assert_called_once()

def test_remove_indexsets_pass_noremovable(mocker,capsys) -> None:
    """clean test_remove_indexsets_pass_noremovable function"""
    mock_response = Mock()
    mock_response.status_code = 204
    mock_response.text = ''
    mock_response.raise_for_status = Mock()
    mocker.patch('src.clean.get_list_all_index_sets_ids', return_value = [])
    result = remove_indexsets(*MOCK_REMOVE_INDEXSETS_ARGS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing index sets for deletion\n"
        "No index sets to delete\n"
        "[Done] processing index sets for deletion.\n\n"
    )
    assert captured.out == expected_output
    assert result is True

def test_remove_indexsets_fail_to_delete( mocked_patches, mocker, capsys) -> None:
    """clean test_remove_indexsets_fail_to_delete function"""
    mock_gen_list_index_set_names_to_delete, mock_get_list_index_set_ids_to_delete, \
        mock_get_list_builtin_index_set_ids, mock_get_list_all_index_sets_ids = mocked_patches
    mock_get_list_all_index_sets_ids.return_value = MOCK_LIST_ALL_INDEX_SETS_IDS
    mock_get_list_builtin_index_set_ids.return_value = MOCK_LIST_BUILTIN_INDEX_SET_IDS
    mock_get_list_index_set_ids_to_delete.return_value = MOCK_LIST_INDEX_SET_IDS_TO_DELETE
    mock_gen_list_index_set_names_to_delete.return_value = MOCK_LIST_INDEX_SET_NAMES_TO_DELETE
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = ''
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.delete', return_value=mock_response)
    with pytest.raises(SystemExit) as e:
        remove_indexsets(*MOCK_REMOVE_INDEXSETS_ARGS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing index sets for deletion\n"
        f"{len(MOCK_LIST_INDEX_SET_IDS_TO_DELETE)} Index Sets found\n"
        f"Removing IndexSet Ids {MOCK_LIST_INDEX_SET_IDS_TO_DELETE}\n"
        f"Removing IndexSet Titles {MOCK_LIST_INDEX_SET_NAMES_TO_DELETE}\n"
        f"[ERROR] Failed to delete input: {MOCK_LIST_INDEX_SET_IDS_TO_DELETE[0]}\n"
    )
    assert captured.out == expected_output
    assert e.value.code == 1
    mock_get_list_all_index_sets_ids.assert_called_once()
    mock_get_list_builtin_index_set_ids.assert_called_once()
    mock_gen_list_index_set_names_to_delete.assert_called_once()

def test_remove_indexsets_fail_request_exception(mocked_patches, mocker, capsys) -> None:
    """clean test_remove_indexsets_fail_request_exception"""
    mock_gen_list_index_set_names_to_delete, mock_get_list_index_set_ids_to_delete, \
        mock_get_list_builtin_index_set_ids, mock_get_list_all_index_sets_ids = mocked_patches
    mock_get_list_all_index_sets_ids.return_value = MOCK_LIST_ALL_INDEX_SETS_IDS
    mock_get_list_builtin_index_set_ids.return_value = MOCK_LIST_BUILTIN_INDEX_SET_IDS
    mock_get_list_index_set_ids_to_delete.return_value = MOCK_LIST_INDEX_SET_IDS_TO_DELETE
    mock_gen_list_index_set_names_to_delete.return_value = MOCK_LIST_INDEX_SET_NAMES_TO_DELETE
    mocker.patch('requests.delete', side_effect=requests.exceptions.RequestException("Connection error"))
    with pytest.raises(SystemExit) as e:
        remove_indexsets(*MOCK_REMOVE_INDEXSETS_ARGS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing index sets for deletion\n"
        f"{len(MOCK_LIST_INDEX_SET_IDS_TO_DELETE)} Index Sets found\n"
        f"Removing IndexSet Ids {MOCK_LIST_INDEX_SET_IDS_TO_DELETE}\n"
        f"Removing IndexSet Titles {MOCK_LIST_INDEX_SET_NAMES_TO_DELETE}\n"
        f"[ERROR] Request error in remove_indexsets: Connection error\n"
    )
    assert captured.out == expected_output
    assert e.value.code == 1
    mock_get_list_all_index_sets_ids.assert_called_once()
    mock_get_list_builtin_index_set_ids.assert_called_once()
    mock_gen_list_index_set_names_to_delete.assert_called_once()

# Test: ValueError (though unlikely here, covered for completeness)
def test_remove_indexsets_value_error(mocked_patches, mocker, capsys) -> None:
    """clean test_remove_indexsets_value_error"""
    mock_gen_list_index_set_names_to_delete, mock_get_list_index_set_ids_to_delete, \
        mock_get_list_builtin_index_set_ids, mock_get_list_all_index_sets_ids = mocked_patches
    mock_get_list_all_index_sets_ids.return_value = MOCK_LIST_ALL_INDEX_SETS_IDS
    mock_get_list_builtin_index_set_ids.return_value = MOCK_LIST_BUILTIN_INDEX_SET_IDS
    mock_get_list_index_set_ids_to_delete.return_value = MOCK_LIST_INDEX_SET_IDS_TO_DELETE
    mock_gen_list_index_set_names_to_delete.return_value = MOCK_LIST_INDEX_SET_NAMES_TO_DELETE
    mocker.patch('requests.delete', side_effect=ValueError("Decoding error"))
    with pytest.raises(SystemExit) as e:
        remove_indexsets(*MOCK_REMOVE_INDEXSETS_ARGS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing index sets for deletion\n"
        f"{len(MOCK_LIST_INDEX_SET_IDS_TO_DELETE)} Index Sets found\n"
        f"Removing IndexSet Ids {MOCK_LIST_INDEX_SET_IDS_TO_DELETE}\n"
        f"Removing IndexSet Titles {MOCK_LIST_INDEX_SET_NAMES_TO_DELETE}\n"
        f"[ERROR] JSON decoding error in remove_indexsets: Decoding error\n"
    )
    assert captured.out == expected_output
    assert e.value.code == 1
    mock_get_list_all_index_sets_ids.assert_called_once()
    mock_get_list_builtin_index_set_ids.assert_called_once()
    mock_gen_list_index_set_names_to_delete.assert_called_once()
