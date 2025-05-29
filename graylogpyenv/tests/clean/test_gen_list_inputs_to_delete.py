"""clean test_gen_list_inputs_to_delete module"""
from unittest.mock import patch, Mock
import json
import requests
import pytest

from src.clean import gen_list_inputs_to_delete

MOCK_FAKE_URL = "http://test-url.com"
MOCK_HEADERS = {"Authorization": "Bearer token"}

@patch('src.clean.requests.get')
def test_gen_list_inputs_to_delete_pass(mock_get) -> None:
    """clean test_gen_list_inputs_to_delete_pass function"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = json.dumps({
        "inputs": [
            {"id": "123", "title": "input1"},
            {"id": "456", "title": "input2"}
        ]
    })
    mock_get.return_value = mock_response
    with patch('src.clean.jq') as mock_jq:
        mock_jq.side_effect = lambda expr, \
            data: [item['id'] for item in data['inputs']] \
            if 'id' in expr else [item['title'] \
            for item in data['inputs']]
        ids, titles = gen_list_inputs_to_delete(MOCK_FAKE_URL, MOCK_HEADERS)
        assert ids == ["123", "456"]
        assert titles == ["input1", "input2"]

@patch('src.clean.requests.get')
def test_gen_list_inputs_to_delete_fail_requests_exception(mock_get,capsys) -> None:
    """clean test_gen_list_inputs_to_delete_fail_requests_exception function"""
    mock_request_exception = "404 Client Error"
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.exceptions.RequestException(mock_request_exception)
    mock_get.return_value = mock_response
    with pytest.raises(SystemExit):
        gen_list_inputs_to_delete(MOCK_FAKE_URL, MOCK_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        f"[ERROR] Request error in gen_list_inputs_to_delete: {mock_request_exception}\n\n"
    )
    assert captured.out == expected_output

@patch('src.clean.requests.get')
def test_gen_list_inputs_to_delete_fail_json_decode_error(mock_get,capsys) -> None:
    """clean test_gen_list_inputs_to_delete_fail_json_decode_error function"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "not-json"
    mock_get.return_value = mock_response
    with pytest.raises(SystemExit):
        gen_list_inputs_to_delete(MOCK_FAKE_URL, MOCK_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "[ERROR] JSON decoding error in gen_list_inputs_to_delete: Expecting value: line 1 column 1 (char 0)\n\n"
    )
    assert captured.out == expected_output
