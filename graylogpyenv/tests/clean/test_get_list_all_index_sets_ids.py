"""Module:tests.clean.test_get_list_all_index_sets_ids"""
import json
import pytest

from src.clean import get_list_all_index_sets_ids
from tests.common.test_common import mock_get_response
from tests.common.test_common import MOCK_DICT_GET_HEADERS
from tests.common.test_common import MOCK_STR_INDEXSETS_URL

MOCK_JQ_RETURN = ['index1', 'index2']

def test_get_list_all_index_sets_ids_pass(mocker) -> None:
    """Function:test_get_list_all_index_sets_ids_pass"""
    mock_response = mock_get_response(200,'{"indexes": [{"id": "index1"}, {"id": "index2"}]}')
    mocker.patch('requests.get', return_value=mock_response)
    mocker.patch('json.loads', return_value=json.loads(mock_response.text))
    mocker.patch('src.clean.jq', return_value=MOCK_JQ_RETURN)
    result = get_list_all_index_sets_ids(MOCK_STR_INDEXSETS_URL, MOCK_DICT_GET_HEADERS)
    assert result == ['index1', 'index2']

def test_get_list_all_index_sets_ids_non_200_response_fail(mocker) -> None:
    """Function:test_get_list_all_index_sets_ids_non_200_response_fail"""
    mock_response = mock_get_response(404,'{"indexes": [{"id": "index1"}, {"id": "index2"}]}')
    mocker.patch('requests.get', return_value=mock_response)
    mocker.patch('json.loads', return_value=json.loads(mock_response.text))
    mocker.patch('src.clean.jq', return_value=MOCK_JQ_RETURN)
    with pytest.raises(SystemExit) as e:
        get_list_all_index_sets_ids(MOCK_STR_INDEXSETS_URL, MOCK_DICT_GET_HEADERS)
    assert e.type == SystemExit
    assert e.value.code == 1
