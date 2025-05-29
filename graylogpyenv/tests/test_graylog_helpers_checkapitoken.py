import pytest
import json
from unittest.mock import patch, Mock
import requests
from src.graylog_helpers import check_api_token

VALID_TEST_URL_NONEXIST = "http://graylog.example.com"
HEADERS = {"Authorization": f"Basic {"encoded_token"}", "Content-Type": "application/json"}
VALID_RESPONSE_DATA = {"string": {"facility":"graylog-server","codename": "string","node_id": "string",
    "cluster_id":"string","version":"string","started_at":"timestamp","hostname":"string","lifecycle":"running",
    "lb_status":"alive","timezone":"string","operating_system":"string","is_leader":"true","is_processing":"true"}}
INVALID_RESPONSE_DATA = {"badval":"fail"}

def test_check_apitoken_pass_mocked_valid_response(capsys,requests_mock):
    args = [VALID_TEST_URL_NONEXIST,HEADERS]
    requests_mock.get(VALID_TEST_URL_NONEXIST, json=VALID_RESPONSE_DATA, status_code=200)
    actual_data = check_api_token(args)
    captured = capsys.readouterr()
    expected_output = (
        "Verify api token authenticates and cluster is up.\n"
        "[Done] Token authenticated to cluster and cluster is up.\n\n"
    )
    assert actual_data == True
    assert captured.out == expected_output

def test_check_apitoken_fail_mocked_invalid_response(requests_mock):
    args = [VALID_TEST_URL_NONEXIST,HEADERS]
    requests_mock.get(VALID_TEST_URL_NONEXIST, json=INVALID_RESPONSE_DATA, status_code=200)
    actual_data = check_api_token(args)
    assert f"[ERROR] cluster status is not ok. Status:" in actual_data

def test_check_apitoken_fail_mocked_response_not_200(requests_mock):
    args = [VALID_TEST_URL_NONEXIST,HEADERS]
    requests_mock.get(VALID_TEST_URL_NONEXIST, json=INVALID_RESPONSE_DATA, status_code=404)
    actual_data = check_api_token(args)
    assert f"[ERROR] Testing api token failed. Response code:404" in actual_data

@pytest.fixture
def valid_args():
    return [
        VALID_TEST_URL_NONEXIST, HEADERS
    ]

def test_check_apitoken_fail_request_exception(valid_args):
    with patch("src.graylog_helpers.requests.get", side_effect=requests.exceptions.RequestException("BAD!")):
        result = check_api_token(valid_args)
        assert "[ERROR]" in result and "BAD!" in result

def test_check_apitoken_fail_json_decode_exception(valid_args):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "INVALID_JSON"

    with patch("src.graylog_helpers.requests.get", return_value=mock_response), \
         patch("src.graylog_helpers.jq") as mock_jq:
        # force json.loads to raise a JSONDecodeError
        with patch("src.graylog_helpers.json.loads", side_effect=json.JSONDecodeError("Expecting value", "doc", 0)):
            result = check_api_token(valid_args)
            assert "problem decoding json" in result.lower()

def test_check_api_token_fail_generic_exception(valid_args):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = json.dumps([{"lifecycle": "running"}])

    # Simulate an unknown error in jq or any other part of the function
    with patch("src.graylog_helpers.requests.get", return_value=mock_response), \
         patch("src.graylog_helpers.jq", side_effect=Exception("Something weird happened")):
        result = check_api_token(valid_args)
        assert "[ERROR]" in result and "Something weird happened" in result