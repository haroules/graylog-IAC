"""Module:tests.setup.test_create_static_fields"""
import requests
import pytest

from src.setup import create_static_fields
from tests.common.test_common import mock_get_response
from tests.common.test_common import shared_asserts
from tests.common.test_common import MOCK_DICT_POST_HEADERS
from tests.common.test_common import MOCK_DICT_GET_HEADERS
from tests.common.test_common import BOOL_VERBOSE_TRUE
from tests.common.test_common import MOCK_STR_INDEXSETS_URL

MOCK_GET_API_RETURN = {"inputs": [ { "id": "input_id", "title": "input_title_1", "global": True, "name": "input_name_1" } ]}
MOCK_POST_API_RETURN = {"key":"input","value":"input_name_1"}

def test_create_static_fields_verbose_success(mocker,capsys) -> None:
    """Function:test_create_static_fields_verbose_success"""
    mock_response = mock_get_response(200,MOCK_GET_API_RETURN)
    mocker.patch('requests.get', return_value=mock_response)
    mocker.patch('json.loads', return_value=MOCK_GET_API_RETURN)
    mocker.patch('src.setup.jq', return_value=[['input_title_1','input_id']])
    mock_post_response = mock_get_response(201,MOCK_POST_API_RETURN)
    mocker.patch('requests.post', return_value=mock_post_response)
    create_static_fields(BOOL_VERBOSE_TRUE,MOCK_STR_INDEXSETS_URL,MOCK_DICT_GET_HEADERS,MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing static fields\n"
        "  1 Static fields to process.\n"
        '  Static field added: {"key":"input","value":"input_title_1"}\n'
        "[Done] Processing static fields.\n\n"
    )
    assert captured.out == expected_output

def test_create_static_fields_fail_non_200_get_inputs(mocker,capsys) -> None:
    """Function:test_create_static_fields_fail_non_200_get_inputs"""
    mock_response = mock_get_response(404,"Not Found")
    mocker.patch('requests.get', return_value=mock_response)
    with pytest.raises(SystemExit) as e:
        create_static_fields(BOOL_VERBOSE_TRUE,MOCK_STR_INDEXSETS_URL,MOCK_DICT_GET_HEADERS,MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing static fields\n"
        f"[ERROR] API call to: {MOCK_STR_INDEXSETS_URL} Failed. Message: {mock_response.text}\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_create_static_fields_fail_no_inputs(mocker,capsys) -> None:
    """Function:test_create_static_fields_fail_no_inputs"""
    mock_response = mock_get_response(200,MOCK_GET_API_RETURN)
    mocker.patch('requests.get', return_value=mock_response)
    mocker.patch('json.loads', return_value=[])
    mocker.patch('src.setup.jq', return_value=[])
    with pytest.raises(SystemExit) as e:
        create_static_fields(BOOL_VERBOSE_TRUE,MOCK_STR_INDEXSETS_URL,MOCK_DICT_GET_HEADERS,MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing static fields\n"
        "[ERROR] No inputs found. Exiting\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_create_static_fields_fields_fail_non_201(mocker,capsys) -> None:
    """Function:test_create_static_fields_fail_non_201"""
    mock_response = mock_get_response(200,MOCK_GET_API_RETURN)
    mocker.patch('requests.get', return_value=mock_response)
    mocker.patch('json.loads', return_value=MOCK_GET_API_RETURN)
    mocker.patch('src.setup.jq', return_value=[['input_title_1','input_id']])
    mock_post_response = mock_get_response(400,"Failed add")
    mocker.patch('requests.post', return_value=mock_post_response)
    with pytest.raises(SystemExit) as e:
        create_static_fields(BOOL_VERBOSE_TRUE,MOCK_STR_INDEXSETS_URL,MOCK_DICT_GET_HEADERS,MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing static fields\n"
        "  1 Static fields to process.\n"
        f"[ERROR] Add static field failed. Message:{mock_post_response.text}\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_create_static_fields_fields_fail_json_decode(mocker,capsys) -> None:
    """Function:test_create_static_fields_fail_json_decode"""
    mock_response = mock_get_response(200,"Bad response")
    mocker.patch('requests.get', return_value=mock_response)
    with pytest.raises(SystemExit) as e:
        create_static_fields(BOOL_VERBOSE_TRUE,MOCK_STR_INDEXSETS_URL,MOCK_DICT_GET_HEADERS,MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    message = "[ERROR] There was a problem decoding json in create_static_fields:"
    expected_output = (
        "Processing static fields\n"
        f"{message} Expecting value: line 1 column 1 (char 0)\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_create_static_fields_fields_fail_request_exception(mocker,capsys) -> None:
    """Function:test_create_static_fields_fail_request_exception"""
    mocker.patch('requests.get', side_effect=requests.exceptions.RequestException("Connection error"))
    with pytest.raises(SystemExit) as e:
        create_static_fields(BOOL_VERBOSE_TRUE,MOCK_STR_INDEXSETS_URL,MOCK_DICT_GET_HEADERS,MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing static fields\n"
        "[ERROR] Request error in create_static_fields: Connection error\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
