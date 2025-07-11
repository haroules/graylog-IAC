"""Module:tests.setup.test_check_extractor_exists"""
import os
import json
import requests
import pytest

from src.setup import check_extractor_exists
from tests.common.test_common import shared_asserts
from tests.common.test_common import mock_get_response
from tests.common.test_common import BOOL_VERBOSE_TRUE
from tests.common.test_common import MOCK_DICT_GET_HEADERS
from tests.common.test_common import MOCK_STR_INPUTS_URL

MOCK_GET_API_RETURN = { "total": 0, "extractors": [] }
MOCK_GET_API_RETURN_EXISTING = { "total": 1, "extractors": [{"title": "samplehost_extractor"}] }
MOCK_EXTRACTOR_ID = "extractor_id_string"

CWD = os.getcwd()
PARENTCWD=os.path.dirname(CWD)
XTRCTRCONFIGFILE = CWD + "/tests/test-configs/extractors/xtrctr_samplehost.json"

def test_check_extractor_exists_success_not_existing(mocker) -> None:
    """Function:test_check_extractor_exists_success_not_existing"""
    mock_response = mock_get_response(200,json.dumps(MOCK_GET_API_RETURN))
    mocker.patch('requests.get', return_value=mock_response)
    returnval = check_extractor_exists(BOOL_VERBOSE_TRUE,MOCK_EXTRACTOR_ID,
                    XTRCTRCONFIGFILE,MOCK_STR_INPUTS_URL,MOCK_DICT_GET_HEADERS)
    assert returnval == ["samplehost_extractor"]

def test_check_extractor_exists_success_existing(mocker,capsys) -> None:
    """FUnction:test_check_extractor_exists_success_existing"""
    mock_response = mock_get_response(200,json.dumps(MOCK_GET_API_RETURN_EXISTING))
    mocker.patch('requests.get', return_value=mock_response)
    returnval = check_extractor_exists(BOOL_VERBOSE_TRUE,MOCK_EXTRACTOR_ID,
                    XTRCTRCONFIGFILE,MOCK_STR_INPUTS_URL,MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    expected_output = "     Extractor ['samplehost_extractor'] already exists\n"
    assert captured.out == expected_output
    assert returnval is True

def test_check_extractor_exists_fail_filenotfound(mocker,capsys) -> None:
    """Function:test_check_extractor_exists_fail_filenotfound"""
    mock_response = mock_get_response(200,json.dumps(MOCK_GET_API_RETURN_EXISTING))
    mocker.patch('requests.get', return_value=mock_response)
    with pytest.raises(SystemExit) as e:
        check_extractor_exists(BOOL_VERBOSE_TRUE,MOCK_EXTRACTOR_ID,"bad_path",MOCK_STR_INPUTS_URL,MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    message = "[ERROR] File or directory not found in check_extractor_exists:"
    expected_output = f"{message} [Errno 2] No such file or directory: "
    assert expected_output in captured.out
    assert e.value.code == 1
    assert e.type == SystemExit

def test_check_extractor_exists_fail_request_exception(mocker,capsys) -> None:
    """Function:test_check_extractor_exists_fail_request_exception"""
    mocker.patch('requests.get', side_effect=requests.exceptions.RequestException("Connection error"))
    with pytest.raises(SystemExit) as e:
        check_extractor_exists(BOOL_VERBOSE_TRUE,MOCK_EXTRACTOR_ID,XTRCTRCONFIGFILE,MOCK_STR_INPUTS_URL,MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    expected_output = "[ERROR] Request error in check_extractor_exists: Connection error\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
