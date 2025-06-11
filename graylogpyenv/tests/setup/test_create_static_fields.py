"""tests.setup test_create_static_fields module"""
from unittest.mock import Mock
import requests
import pytest

from src.setup import create_static_fields
from tests.common.test_common import shared_asserts

MOCK_INPUTS_URL="https://mock.api/indexsets"
MOCK_DICT_POST_HEADERS={"Authorization": "Bearer mock"}
MOCK_DICT_GET_HEADERS={"Authorization": "Bearer mock"}
MOCK_BOOL_VEBOSE=True
MOCK_GET_API_RETURN = {"inputs": [ { "id": "input_id", "title": "input_title_1", "global": True, "name": "input_name_1" } ]}
MOCK_POST_API_RETURN = {"key":"input","value":"input_name_1"}

def test_create_static_fields_verbose_success(mocker,capsys) -> None:
    """tests.setup.test_create_static_fields_verbose_success function"""
    mock_get_response = Mock()
    mock_get_response.status_code = 200
    mock_get_response.text = MOCK_GET_API_RETURN
    mock_get_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_get_response)
    mocker.patch('json.loads', return_value=MOCK_GET_API_RETURN)
    mocker.patch('src.setup.jq', return_value=[['input_title_1','input_id']])
    mock_post_response = Mock()
    mock_post_response.status_code = 201
    mock_post_response.text = MOCK_POST_API_RETURN
    mock_post_response.raise_for_status = Mock()
    mocker.patch('requests.post', return_value=mock_post_response)
    create_static_fields(MOCK_BOOL_VEBOSE,MOCK_INPUTS_URL,MOCK_DICT_GET_HEADERS,MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing static fields\n"
        "  1 Static fields to process.\n"
        '  Static field added: {"key":"input","value":"input_title_1"}\n'
        "[Done] Processing static fields.\n\n"
    )
    assert captured.out == expected_output

def test_create_static_fields_fail_non_200_get_inputs(mocker,capsys) -> None:
    """tests.setup.test_create_static_fields_fail_non_200_get_inputs function"""
    mock_get_response = Mock()
    mock_get_response.status_code = 404
    mock_get_response.text = "Not Found"
    mock_get_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_get_response)
    with pytest.raises(SystemExit) as e:
        create_static_fields(MOCK_BOOL_VEBOSE,MOCK_INPUTS_URL,MOCK_DICT_GET_HEADERS,MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing static fields\n"
        f"[ERROR] API call to: {MOCK_INPUTS_URL} Failed. Message: {mock_get_response.text}\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_create_static_fields_fail_no_inputs(mocker,capsys) -> None:
    """stests.setup.test_create_static_fields_fail_no_inputs function"""
    mock_get_response = Mock()
    mock_get_response.status_code = 200
    mock_get_response.text = MOCK_GET_API_RETURN
    mock_get_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_get_response)
    mocker.patch('json.loads', return_value=[])
    mocker.patch('src.setup.jq', return_value=[])
    with pytest.raises(SystemExit) as e:
        create_static_fields(MOCK_BOOL_VEBOSE,MOCK_INPUTS_URL,MOCK_DICT_GET_HEADERS,MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing static fields\n"
        "[ERROR] No inputs found. Exiting\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_create_static_fields_fields_fail_non_201(mocker,capsys) -> None:
    """tests.setup.test_create_static_fields_fail_non_201 function"""
    mock_get_response = Mock()
    mock_get_response.status_code = 200
    mock_get_response.text = MOCK_GET_API_RETURN
    mock_get_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_get_response)
    mocker.patch('json.loads', return_value=MOCK_GET_API_RETURN)
    mocker.patch('src.setup.jq', return_value=[['input_title_1','input_id']])
    mock_post_response = Mock()
    mock_post_response.status_code = 400
    mock_post_response.text = "Failed add"
    mock_post_response.raise_for_status = Mock()
    mocker.patch('requests.post', return_value=mock_post_response)
    with pytest.raises(SystemExit) as e:
        create_static_fields(MOCK_BOOL_VEBOSE,MOCK_INPUTS_URL,MOCK_DICT_GET_HEADERS,MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing static fields\n"
        "  1 Static fields to process.\n"
        f"[ERROR] Add static field failed. Message:{mock_post_response.text}\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_create_static_fields_fields_fail_json_decode(mocker,capsys) -> None:
    """stests.setup.test_create_static_fields_fail_json_decode function"""
    mock_get_response = Mock()
    mock_get_response.status_code = 200
    mock_get_response.text = "Bad response"
    mock_get_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_get_response)
    with pytest.raises(SystemExit) as e:
        create_static_fields(MOCK_BOOL_VEBOSE,MOCK_INPUTS_URL,MOCK_DICT_GET_HEADERS,MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    message = "[ERROR] There was a problem decoding json in create_static_fields:"
    expected_output = (
        "Processing static fields\n"
        f"{message} Expecting value: line 1 column 1 (char 0)\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_create_static_fields_fields_fail_request_exception(mocker,capsys) -> None:
    """tests.setup.test_create_static_fields_fail_request_exception function"""
    mock_get_response = Mock()
    mock_get_response.status_code = 200
    mock_get_response.text = MOCK_GET_API_RETURN
    mock_get_response.raise_for_status = Mock()
    mocker.patch('requests.get', side_effect=requests.exceptions.RequestException("Connection error"))
    with pytest.raises(SystemExit) as e:
        create_static_fields(MOCK_BOOL_VEBOSE,MOCK_INPUTS_URL,MOCK_DICT_GET_HEADERS,MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing static fields\n"
        "[ERROR] Request error in create_static_fields: Connection error\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
