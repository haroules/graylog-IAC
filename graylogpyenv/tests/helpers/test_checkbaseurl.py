"""Module:tests.helpers.test_checkbaseurl"""
from src.helpers import check_graylog_baseurl

from tests.common.test_common import MOCK_TEST_URL
from tests.common.test_common import MOCK_TOKEN
from tests.common.test_common import MOCK_SCRIPT

MALFORMED_TEST_URL = "htps://graylog.123"
VALID_CWD = "/path/notused"

def test_check_graylog_baseurl_pass_valid_response(capsys,requests_mock) -> None:
    """Function:test_check_graylog_baseurl_pass_valid_response"""
    args = [MOCK_SCRIPT, MOCK_TOKEN, MOCK_TEST_URL, VALID_CWD]
    mock_response_data = {"cluster_id":"some_cluster_id","node_id":"some_node_id","version":"version_string","tagline":"string"}
    requests_mock.get(MOCK_TEST_URL, json=mock_response_data, status_code=200)
    actual_data = check_graylog_baseurl(args)
    captured = capsys.readouterr()
    expected_output = (
        "Verify graylog baseurl.\n"
        "[Done] Verify graylog baseurl.\n\n"
    )
    assert actual_data is True
    assert captured.out == expected_output

def test_check_graylog_baseurl_fail_invalid_response(requests_mock) -> None:
    """Function:test_check_graylog_baseurl_fail_invalid_response"""
    args = [MOCK_SCRIPT, MOCK_TOKEN, MOCK_TEST_URL, VALID_CWD]
    mock_response_data = {"badval":"fail"}
    requests_mock.get(MOCK_TEST_URL, json=mock_response_data, status_code=200)
    actual_data = check_graylog_baseurl(args)
    assert f"[ERROR] {MOCK_TEST_URL} Didn't provide expected response. Recieved:" in actual_data

def test_check_graylog_baseurl_fail_jsonresponse(requests_mock) -> None:
    """Function:test_check_graylog_baseurl_fail_jsonresponse"""
    args = [MOCK_SCRIPT, MOCK_TOKEN, MOCK_TEST_URL, VALID_CWD]
    requests_mock.get(MOCK_TEST_URL, status_code=200)
    actual_data = check_graylog_baseurl(args)
    assert "[ERROR] There was a problem decoding json response: " in actual_data

def test_check_graylog_baseurl_fail_validtesturlnonexist() -> None:
    """Function:test_check_graylog_baseurl_fail_validtesturlnonexist"""
    args = [MOCK_SCRIPT, MOCK_TOKEN, MOCK_TEST_URL, VALID_CWD]
    value = check_graylog_baseurl(args)
    expected_output = (
        f"[ERROR] {MOCK_TEST_URL} Didn't respond.\n"
        " Error was:"
    )
    assert expected_output in value

def test_check_graylog_baseurl_fail_malformed_url() -> None:
    """Function:test_check_graylog_baseurl_fail_malformed_url"""
    args = [MOCK_SCRIPT, MOCK_TOKEN, MALFORMED_TEST_URL, VALID_CWD]
    value=check_graylog_baseurl(args)
    assert f"[ERROR] URL appears malformed: {MALFORMED_TEST_URL}" in value
