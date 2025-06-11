"""tests.clean test_remove_inputs module"""
from unittest.mock import patch, Mock
import requests
import pytest

from src.clean import remove_inputs
from tests.common.test_common import shared_asserts

MOCK_BOOL_VERBOSE = True
MOCK_STR_INPUTS_URL = "http://test-url.com/inputs"
MOCK_DICT_GET_HEADERS = {"Authorization": "Bearer token"}
MOCK_DICT_POST_HEADERS = {"Authorization": "Bearer token"}
MOCK_REMOVE_INPUTS_ARGS = [MOCK_BOOL_VERBOSE, MOCK_STR_INPUTS_URL, MOCK_DICT_GET_HEADERS, MOCK_DICT_POST_HEADERS]
MOCK_LIST_INPUTS = (["id1", "id2"], ["Input 1", "Input 2"])
MOCK_FAIL_LIST = (["id1"], ["Input 1"])

@patch('src.clean.requests.delete')
@patch('src.clean.gen_list_inputs_to_delete')
def test_remove_inputs_success_removables(mock_gen_list, mock_delete, capsys) -> None:
    """tests.clean.test_remove_inputs_success_removables function"""
    mock_gen_list.return_value = MOCK_LIST_INPUTS
    mock_response = Mock()
    mock_response.status_code = 204
    mock_delete.return_value = mock_response
    assert remove_inputs(*MOCK_REMOVE_INPUTS_ARGS) is True
    captured = capsys.readouterr()
    expected_output = (
        "Processing inputs for deletion\n"
        f"{len(MOCK_LIST_INPUTS)} Inputs found\n"
        f"Removing Input Ids {MOCK_LIST_INPUTS[0]}\n"
        f"Removing Input Titles {MOCK_LIST_INPUTS[1]}\n"
        "[Done] processing inputs for deletion.\n\n"
    )
    assert captured.out == expected_output

@patch('src.clean.gen_list_inputs_to_delete')
def test_remove_inputs_success_noremovables(mock_gen_list, capsys) -> None:
    """tests.clean.test_remove_inputs_success_noremovables function"""
    mock_gen_list.return_value = ([], [])
    assert remove_inputs(*MOCK_REMOVE_INPUTS_ARGS) is True
    captured = capsys.readouterr()
    expected_output = (
        "Processing inputs for deletion\n"
        "No inputs to delete\n"
        "[Done] processing inputs for deletion.\n\n"
    )
    assert captured.out == expected_output

@patch('src.clean.requests.delete')
@patch('src.clean.gen_list_inputs_to_delete')
def test_remove_inputs_fail_non_204_response(mock_gen_list, mock_delete, capsys) -> None:
    """tests.clean.test_remove_inputs_fail_non_204_response function"""
    mock_gen_list.return_value = MOCK_FAIL_LIST
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.raise_for_status.return_value = None
    mock_delete.return_value = mock_response
    with pytest.raises(SystemExit) as e:
        remove_inputs(*MOCK_REMOVE_INPUTS_ARGS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing inputs for deletion\n"
        f"{len(MOCK_FAIL_LIST[0])} Inputs found\n"
        f"Removing Input Ids {MOCK_FAIL_LIST[0]}\n"
        f"Removing Input Titles {MOCK_FAIL_LIST[1]}\n"
        "[ERROR] Failed to delete input: id1\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

@patch('src.clean.requests.delete')
@patch('src.clean.gen_list_inputs_to_delete')
def test_remove_inputs_fail_request_exception(mock_gen_list, mock_delete, capsys) -> None:
    """tests.clean.test_remove_inputs_fail_request_exception function"""
    mock_gen_list.return_value = MOCK_FAIL_LIST
    mock_delete.side_effect = requests.exceptions.RequestException("Network error")
    with pytest.raises(SystemExit) as e:
        remove_inputs(*MOCK_REMOVE_INPUTS_ARGS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing inputs for deletion\n"
        f"{len(MOCK_FAIL_LIST[0])} Inputs found\n"
        f"Removing Input Ids {MOCK_FAIL_LIST[0]}\n"
        f"Removing Input Titles {MOCK_FAIL_LIST[1]}\n"
        "Request error in remove_inputs: Network error\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

@patch('src.clean.requests.delete')
@patch('src.clean.gen_list_inputs_to_delete')
def test_remove_inputs_fail_value_error(mock_gen_list, mock_delete, capsys) -> None:
    """tests.clean.test_remove_inputs_fail_value_error function"""
    mock_gen_list.return_value = MOCK_FAIL_LIST
    mock_delete.side_effect = ValueError("JSON error")
    with pytest.raises(SystemExit) as e:
        remove_inputs(*MOCK_REMOVE_INPUTS_ARGS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing inputs for deletion\n"
        f"{len(MOCK_FAIL_LIST[0])} Inputs found\n"
        f"Removing Input Ids {MOCK_FAIL_LIST[0]}\n"
        f"Removing Input Titles {MOCK_FAIL_LIST[1]}\n"
        "JSON decoding error in remove_inputs: JSON error\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
