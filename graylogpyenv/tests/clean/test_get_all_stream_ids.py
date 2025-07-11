"""Module:tests.clean.test_get_all_stream_ids"""
import json

from src.clean import get_list_all_stream_ids
from tests.common.test_common import mock_get_response
from tests.common.test_common import MOCK_DICT_GET_HEADERS
from tests.common.test_common import MOCK_STR_STREAMS_URL

MOCK_JQ_RETURN = ['stream1', 'stream2']

def test_get_list_all_stream_ids_pass(mocker) -> None:
    """Function:test_get_list_all_stream_ids_pass"""
    mock_response = mock_get_response(200,'{"streams": [{"id": "stream1"}, {"id": "stream2"}]}')
    mocker.patch('requests.get', return_value=mock_response)
    mocker.patch('json.loads', return_value=json.loads(mock_response.text))
    mocker.patch('src.clean.jq', return_value=MOCK_JQ_RETURN)
    result = get_list_all_stream_ids(MOCK_STR_STREAMS_URL, MOCK_DICT_GET_HEADERS)
    assert result == ['stream1', 'stream2']
