"""clean test_get_all_stream_ids module"""
import json
from unittest.mock import Mock

from src.clean import get_list_all_stream_ids
MOCK_JQ_RETURN = ['stream1', 'stream2']
MOCK_FAKE_URL = "http://test-url.com"
MOCK_DICT_GET_HEADERS = {"Authorization": "Bearer token"}

def test_get_list_all_stream_ids_pass(mocker) -> None:
    """clean test_get_list_all_stream_ids_pass function"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = '{"streams": [{"id": "stream1"}, {"id": "stream2"}]}'
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_response)
    mocker.patch('json.loads', return_value=json.loads(mock_response.text))
    mocker.patch('src.clean.jq', return_value=MOCK_JQ_RETURN)
    result = get_list_all_stream_ids(MOCK_FAKE_URL, MOCK_DICT_GET_HEADERS)
    assert result == ['stream1', 'stream2']
