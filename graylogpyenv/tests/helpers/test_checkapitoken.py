"""Module:tests.helpers.test_checkapitoken"""
import json
from unittest.mock import patch
import requests
import pytest

from src.helpers import check_api_token
from tests.common.test_common import mock_get_response
from tests.common.test_common import MOCK_DICT_GET_HEADERS
from tests.common.test_common import MOCK_TEST_URL

VALID_RESPONSE_DATA = {"string": {"facility":"graylog-server","codename": "string","node_id": "string",
    "cluster_id":"string","version":"string","started_at":"timestamp","hostname":"string","lifecycle":"running",
    "lb_status":"alive","timezone":"string","operating_system":"string","is_leader":"true","is_processing":"true"}}
INVALID_RESPONSE_DATA = {"badval":"fail"}

def test_check_apitoken_pass_valid_response(capsys,requests_mock) -> None:
    """Function:test_check_apitoken_pass_valid_response"""
    args = [MOCK_TEST_URL,MOCK_DICT_GET_HEADERS]
    requests_mock.get(MOCK_TEST_URL, json=VALID_RESPONSE_DATA, status_code=200)
    actual_data = check_api_token(args)
    captured = capsys.readouterr()
    expected_output = (
        "Verify api token authenticates and cluster is up.\n"
        "[Done] Token authenticated to cluster and cluster is up.\n\n"
    )
    assert actual_data is True
    assert captured.out == expected_output

def test_check_apitoken_fail_invalid_response(requests_mock) -> None:
    """Function:test_check_apitoken_fail_invalid_response"""
    args = [MOCK_TEST_URL,MOCK_DICT_GET_HEADERS]
    requests_mock.get(MOCK_TEST_URL, json=INVALID_RESPONSE_DATA, status_code=200)
    actual_data = check_api_token(args)
    assert "[ERROR] cluster status is not ok. Status:" in actual_data

def test_check_apitoken_fail_response_not_200(requests_mock) -> None:
    """Function:test_check_apitoken_fail_response_not_200"""
    args = [MOCK_TEST_URL,MOCK_DICT_GET_HEADERS]
    requests_mock.get(MOCK_TEST_URL, json=INVALID_RESPONSE_DATA, status_code=404)
    actual_data = check_api_token(args)
    assert "[ERROR] Testing api token failed. Response code:404" in actual_data

@pytest.fixture(name="mocked_args")
def valid_args():
    """Function:valid_args"""
    return [
        MOCK_TEST_URL, MOCK_DICT_GET_HEADERS
    ]

def test_check_apitoken_fail_request_exception(mocked_args) -> None:
    """Function:test_check_apitoken_fail_request_exception"""
    with patch("src.helpers.requests.get", side_effect=requests.exceptions.RequestException("BAD!")):
        result = check_api_token(mocked_args)
        assert "[ERROR]" in result and "BAD!" in result

def test_check_apitoken_fail_json_decode_exception(mocked_args) -> None:
    """Function:test_check_apitoken_fail_json_decode_exception"""
    mock_response = mock_get_response(200,"INVALID_JSON")
    with patch("src.helpers.requests.get", return_value=mock_response), \
         patch("src.helpers.jq"):
        # force json.loads to raise a JSONDecodeError
        with patch("src.helpers.json.loads", side_effect=json.JSONDecodeError("Expecting value", "doc", 0)):
            result = check_api_token(mocked_args)
            assert "problem decoding json" in result.lower()
