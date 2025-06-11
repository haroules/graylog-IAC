"""tests.clean test_get_list_stream_names_to_delete module"""
import json
from unittest.mock import Mock

from src.clean import get_list_stream_names_to_delete

MOCK_LIST_STREAM_IDS = ["00001"]
MOCK_JQ_RETURN = ['stream1']
MOCK_STR_STREAMS_URL = "http://test-url.com/streams"
MOCK_DICT_GET_HEADERS = {"Authorization": "Bearer token"}

def test_get_list_stream_names_to_delete_pass(mocker) -> None:
    '''tests.clean.test_get_list_stream_names_to_delete_pass function'''
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = '{"streams": [{"id": "00001", "title": "stream1"}]}'
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_response)
    mocker.patch('json.loads', return_value=json.loads(mock_response.text))
    mocker.patch('src.clean.jq', return_value=MOCK_JQ_RETURN)
    result = get_list_stream_names_to_delete(MOCK_LIST_STREAM_IDS, MOCK_STR_STREAMS_URL, MOCK_DICT_GET_HEADERS)
    assert result == MOCK_JQ_RETURN

def test_get_list_stream_names_to_delete_fail_bad_response_code(mocker,capsys) -> None:
    """tests.clean.test_get_list_stream_names_to_delete_fail_bad_response_code function"""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = ''
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_response)
    mock_exit = mocker.patch('sys.exit')
    get_list_stream_names_to_delete(MOCK_LIST_STREAM_IDS, MOCK_STR_STREAMS_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    assert captured.out == "[ERROR] Couldn't find id. 00001\n\n"
    mock_exit.assert_called_once_with(1)
