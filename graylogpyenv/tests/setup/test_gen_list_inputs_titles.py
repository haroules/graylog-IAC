"""Module:tests.setup.test_gen_list_inputs_titles"""
import requests
import pytest

from src.setup import gen_list_inputs_titles
from tests.common.test_common import mock_get_response
from tests.common.test_common import shared_asserts
from tests.common.test_common import MOCK_DICT_GET_HEADERS
from tests.common.test_common import MOCK_STR_INPUTS_URL

MOCK_API_RETURN = {"inputs": [ { "title": "input_title_1", "global": True, "name": "input_name_1" } ] }

def test_gen_list_inputs_titles_pass(mocker) -> None:
    """Function:test_gen_list_inputs_titles_pass"""
    mock_response = mock_get_response(200,MOCK_API_RETURN)
    mocker.patch('requests.get', return_value=mock_response)
    mocker.patch('json.loads', return_value=MOCK_API_RETURN)
    mocker.patch('src.setup.jq', return_value=["input_title_1"])
    return_val = gen_list_inputs_titles(MOCK_STR_INPUTS_URL,MOCK_DICT_GET_HEADERS)
    assert return_val == ["input_title_1"]

def test_gen_list_inputs_titles_fail_non_200_response(mocker,capsys) -> None:
    """Function:test_gen_list_inputs_titles_fail_non_200_response"""
    mock_response = mock_get_response(404,"Bad response")
    mocker.patch('requests.get', return_value=mock_response)
    with pytest.raises(SystemExit) as e:
        gen_list_inputs_titles(MOCK_STR_INPUTS_URL,MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    expected_output = f"[ERROR] API call to: {MOCK_STR_INPUTS_URL} Failed. Message: Bad response\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_gen_list_inputs_titles_fail_json_decode(mocker,capsys) -> None:
    """Function:test_gen_list_inputs_titles_fail_json_decode"""
    mock_response = mock_get_response(200,"Bad response")
    mocker.patch('requests.get', return_value=mock_response)
    with pytest.raises(SystemExit) as e:
        gen_list_inputs_titles(MOCK_STR_INPUTS_URL,MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    message = "[ERROR] There was a problem decoding json in gen_list_inputs_titles:"
    expected_output = f"{message} Expecting value: line 1 column 1 (char 0)\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_gen_list_inputs_titles_fail_request_exception(mocker,capsys) -> None:
    """Function:test_gen_list_inputs_titles_fail_request_exception"""
    mocker.patch('requests.get', side_effect=requests.exceptions.RequestException("Connection error"))
    with pytest.raises(SystemExit) as e:
        gen_list_inputs_titles(MOCK_STR_INPUTS_URL,MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    message = "[ERROR] Request error in gen_list_inputs_titles:"
    expected_output = f"{message} Connection error\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
