"""Module:tests.setup.test_gen_list_extractor_details"""
import os
import json
import requests
import pytest

from src.setup import gen_list_extractor_details
from tests.common.test_common import mock_get_response
from tests.common.test_common import shared_asserts
from tests.common.test_common import MOCK_DICT_GET_HEADERS
from tests.common.test_common import MOCK_STR_INPUTS_URL

MOCK_GET_API_RETURN = {"inputs": [ { "title": "samplehost-input", "global": True,
    "name": "input_samplehost", "id": "input_id_string" } ] }

CWD = os.getcwd()
CONFIGSETFILE= CWD + "/tests/test-configs/configset/configset.json"
with open(CONFIGSETFILE, "r", encoding="utf-8") as file:
    dict_config = json.load(file)

def test_gen_list_extractor_details_success(mocker) -> None:
    """Function:test_gen_list_extractor_details_success"""
    mock_response = mock_get_response(200,json.dumps(MOCK_GET_API_RETURN))
    mocker.patch('requests.get', return_value=mock_response)
    returnval = gen_list_extractor_details(dict_config,MOCK_STR_INPUTS_URL,MOCK_DICT_GET_HEADERS)
    assert returnval == ["input_id_string", '"samplehost-input"', ["xtrctr_samplehost.json"]]

def test_gen_list_extractor_details_fail_non_200_response(mocker,capsys) -> None:
    """Function:test_gen_list_extractor_details_fail_non_200_response"""
    mock_response = mock_get_response(404,"Not Found")
    mocker.patch('requests.get', return_value=mock_response)
    with pytest.raises(SystemExit) as e:
        gen_list_extractor_details(dict_config,MOCK_STR_INPUTS_URL,MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    expected_output = f"[ERROR] API call to: {MOCK_STR_INPUTS_URL} Failed. Message: {mock_response.text}\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_gen_list_extractor_details_fail_request_exception(mocker,capsys) -> None:
    """Function:test_gen_list_extractor_details_fail_request_exception"""
    mocker.patch('requests.get', side_effect=requests.exceptions.RequestException("Connection error"))
    with pytest.raises(SystemExit) as e:
        gen_list_extractor_details(dict_config,MOCK_STR_INPUTS_URL,MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    expected_output = "[ERROR] Request error in gen_list_extractor_details: Connection error\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
