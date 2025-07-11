"""Module:tests.clean.test_get_list_stream_names_to_delete"""
import json

from src.clean import get_list_stream_names_to_delete
from tests.common.test_common import mock_get_response
from tests.common.test_common import MOCK_DICT_GET_HEADERS
from tests.common.test_common import MOCK_STR_STREAMS_URL

MOCK_LIST_STREAM_IDS = ["00001"]
MOCK_JQ_RETURN = ['stream1']

def test_get_list_stream_names_to_delete_pass(mocker) -> None:
    """Function:test_get_list_stream_names_to_delete_pass"""
    mock_response = mock_get_response(200,'{"streams": [{"id": "00001", "title": "stream1"}]}')
    mocker.patch('requests.get', return_value=mock_response)
    mocker.patch('json.loads', return_value=json.loads(mock_response.text))
    mocker.patch('src.clean.jq', return_value=MOCK_JQ_RETURN)
    result = get_list_stream_names_to_delete(MOCK_LIST_STREAM_IDS, MOCK_STR_STREAMS_URL, MOCK_DICT_GET_HEADERS)
    assert result == MOCK_JQ_RETURN

def test_get_list_stream_names_to_delete_fail_bad_response_code(mocker,capsys) -> None:
    """Function:test_get_list_stream_names_to_delete_fail_bad_response_code"""
    mock_response = mock_get_response(404,'')
    mocker.patch('requests.get', return_value=mock_response)
    mock_exit = mocker.patch('sys.exit')
    get_list_stream_names_to_delete(MOCK_LIST_STREAM_IDS, MOCK_STR_STREAMS_URL, MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    assert captured.out == "[ERROR] Couldn't find id. 00001\n\n"
    mock_exit.assert_called_once_with(1)
