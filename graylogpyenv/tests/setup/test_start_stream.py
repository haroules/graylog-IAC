"""Module:tests.setup.test_start_stream"""
import pytest

from src.setup import start_stream
from tests.common.test_common import shared_asserts
from tests.common.test_common import mock_get_response
from tests.common.test_common import MOCK_STR_STREAMS_URL
from tests.common.test_common import MOCK_DICT_POST_HEADERS

def test_start_stream_success(mocker) -> None:
    """Function:test_start_stream_success"""
    mock_response = mock_get_response(204,"")
    mocker.patch('requests.post', return_value=mock_response)
    start_stream("some_stream_id",MOCK_STR_STREAMS_URL,MOCK_DICT_POST_HEADERS)

def test_start_stream_fail_verbose(mocker,capsys) -> None:
    """Function:test_start_stream_fail_verbose"""
    mock_response = mock_get_response(404,"Stream not found")
    mocker.patch('requests.post', return_value=mock_response)
    with pytest.raises(SystemExit) as e:
        start_stream("some_stream_id",MOCK_STR_STREAMS_URL,MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    expected_output = f"[ERROR] Start streams failed. Message: {mock_response.text}\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
