"""helpers test_checkbaseurl module"""
from src.helpers import check_graylog_baseurl

VALID_SCRIPT = "script.py"
VALID_TOKEN = "TOKEN"
VALID_TEST_URL_NONEXIST = "http://graylog.example.com"
MALFORMED_TEST_URL = "htps://graylog.123"
VALID_CWD = "/path/notused"
VERBOSE = False

def test_check_graylog_baseurl_pass_mocked_valid_response(capsys,requests_mock) -> None:
    """helpers test_check_graylog_baseurl_pass_mocked_valid_response function"""
    args = [VALID_SCRIPT, VALID_TOKEN, VALID_TEST_URL_NONEXIST, VALID_CWD]
    mock_response_data = {"cluster_id":"some_cluster_id","node_id":"some_node_id","version":"version_string","tagline":"string"}
    requests_mock.get(VALID_TEST_URL_NONEXIST, json=mock_response_data, status_code=200)
    actual_data = check_graylog_baseurl(args)
    captured = capsys.readouterr()
    expected_output = (
        "Verify graylog baseurl.\n"
        "[Done] Verify graylog baseurl.\n\n"
    )
    assert actual_data is True
    assert captured.out == expected_output

def test_check_graylog_baseurl_fail_mocked_invalid_response(requests_mock) -> None:
    """helpers test_check_graylog_baseurl_fail_mocked_invalid_response function"""
    args = [VALID_SCRIPT, VALID_TOKEN, VALID_TEST_URL_NONEXIST, VALID_CWD]
    mock_response_data = {"badval":"fail"}
    requests_mock.get(VALID_TEST_URL_NONEXIST, json=mock_response_data, status_code=200)
    actual_data = check_graylog_baseurl(args)
    assert "[ERROR] http://graylog.example.com Didn't provide expected response. Recieved:" in actual_data

def test_check_graylog_baseurl_fail_valid_endpoint_bad_url(requests_mock) -> None:
    """helpers test_check_graylog_baseurl_fail_valid_endpoint_bad_url function"""
    args = [VALID_SCRIPT, VALID_TOKEN, VALID_TEST_URL_NONEXIST, VALID_CWD]
    requests_mock.get(VALID_TEST_URL_NONEXIST, status_code=200)
    actual_data = check_graylog_baseurl(args)
    assert "[ERROR] There was a problem decoding json response: " in actual_data

def test_check_graylog_baseurl_fail_validtesturlnonexist() -> None:
    """helpers test_check_graylog_baseurl_fail_validtesturlnonexist function"""
    args = [VALID_SCRIPT, VALID_TOKEN, VALID_TEST_URL_NONEXIST, VALID_CWD]
    value = check_graylog_baseurl(args)
    expected_output = (
        "[ERROR] http://graylog.example.com Didn't respond.\n"
        " Error was:"
    )
    assert expected_output in value

def test_check_graylog_baseurl_fail_malformed_url() -> None:
    """helpers test_check_graylog_baseurl_fail_malformed_url function"""
    args = [VALID_SCRIPT, VALID_TOKEN, MALFORMED_TEST_URL, VALID_CWD]
    value=check_graylog_baseurl(args)
    assert "[ERROR] URL appears malformed: htps://graylog.123" in value
