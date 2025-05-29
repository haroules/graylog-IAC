"""tests.setup test_gen_list_inputs_titles module"""

from unittest.mock import Mock
import requests
import pytest

from src.setup import gen_list_inputs_titles

MOCK_INPUTS_URL="https://mock.api/inputs"
MOCK_DICT_GET_HEADERS={"Authorization": "Bearer mock"}
MOCK_API_RETURN = {"inputs": [ { "title": "input_title_1", "global": True, "name": "input_name_1" } ] }

def test_gen_list_inputs_titles_pass(mocker) -> None:
    """tests.setup test_gen_list_inputs_titles_pass function"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = MOCK_API_RETURN
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_response)
    mocker.patch('json.loads', return_value=MOCK_API_RETURN)
    mocker.patch('src.setup.jq', return_value=["input_title_1"])
    return_val = gen_list_inputs_titles(MOCK_INPUTS_URL,MOCK_DICT_GET_HEADERS)
    assert return_val == ["input_title_1"]

def test_gen_list_inputs_titles_fail_non_200_response(mocker,capsys) -> None:
    """tests.setup test_gen_list_inputs_titles_fail_non_200_response function"""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "Bad response"
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_response)
    with pytest.raises(SystemExit) as e:
        gen_list_inputs_titles(MOCK_INPUTS_URL,MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "[ERROR] API call to: https://mock.api/inputs Failed. Message: Bad response\n"
    )
    assert captured.out == expected_output
    assert e.value.code == 1

def test_gen_list_inputs_titles_fail_json_decode(mocker,capsys) -> None:
    """tests.setup test_gen_list_inputs_titles_fail_json_decode function"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "Bad response"
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_response)
    with pytest.raises(SystemExit) as e:
        gen_list_inputs_titles(MOCK_INPUTS_URL,MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    message = "[ERROR] There was a problem decoding json in gen_list_inputs_titles:"
    expected_output = (
        f"{message} Expecting value: line 1 column 1 (char 0)\n"
    )
    assert captured.out == expected_output
    assert e.value.code == 1

def test_gen_list_inputs_titles_fail_request_exception(mocker,capsys) -> None:
    """tests.setup test_gen_list_inputs_titles_fail_request_exception function"""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "Bad response"
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', side_effect=requests.exceptions.RequestException("Connection error"))
    with pytest.raises(SystemExit) as e:
        gen_list_inputs_titles(MOCK_INPUTS_URL,MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    message = "[ERROR] Request error in gen_list_inputs_titles:"
    expected_output = (
        f"{message} Connection error\n"
    )
    assert captured.out == expected_output
    assert e.value.code == 1
