"""Module:tests.clean.test_get_list_all_builtin_index_set_ids"""
import json
import pytest

from src.clean import get_list_all_builtin_index_set_ids
from tests.common.test_common import mock_get_response
from tests.common.test_common import MOCK_STR_INDEXSETS_URL
from tests.common.test_common import MOCK_DICT_GET_HEADERS

MOCK_JQ_RETURN = ['0001']
MOCK_LIST_BUILTIN_INDEX_SET_NAMES = ["index1", "index2", "index3"]

def test_get_list_all_builtin_index_set_ids_pass(mocker ) -> None:
    """Function:test_get_list_all_builtin_index_set_ids_pass"""
    mock_response = mock_get_response(200,'{"index_sets": [{"id": "0001","title": "index1"}]}')
    mocker.patch('requests.get', return_value=mock_response)
    mocker.patch('json.loads', return_value=json.loads(mock_response.text))
    mocker.patch('src.clean.jq', return_value=MOCK_JQ_RETURN)
    result = get_list_all_builtin_index_set_ids(MOCK_STR_INDEXSETS_URL, MOCK_DICT_GET_HEADERS, ["index1"])
    assert result == ['0001']

def test_get_list_all_builtin_index_set_ids_fail_non_200(mocker) -> None:
    """Function:test_get_list_all_builtin_index_set_ids_fail_non_200"""
    mock_response = mock_get_response(404,'{"index_sets": [{"id": "0001","title": "index1"}]}')
    mocker.patch('requests.get', return_value=mock_response)
    mocker.patch('json.loads', return_value=json.loads(mock_response.text))
    mocker.patch('src.clean.jq', return_value=MOCK_JQ_RETURN)
    with pytest.raises(SystemExit) as e:
        get_list_all_builtin_index_set_ids(MOCK_STR_INDEXSETS_URL, MOCK_DICT_GET_HEADERS, ["index1"])
    assert e.type == SystemExit
    assert e.value.code == 1
