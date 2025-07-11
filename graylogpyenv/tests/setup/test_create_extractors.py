"""Module:tests.setup.test_create_extractors"""
import os
import json
import requests
import pytest

from src.setup import create_extractors

from tests.common.test_common import mock_get_response
from tests.common.test_common import shared_asserts
from tests.common.test_common import BOOL_VERBOSE_TRUE
from tests.common.test_common import MOCK_STR_INPUTS_URL
from tests.common.test_common import MOCK_DICT_GET_HEADERS
from tests.common.test_common import MOCK_DICT_POST_HEADERS

CWD = os.getcwd()
HOSTCONFIGDIR = CWD + "/tests/test-configs/host-config"
XTRCTRCONFIGDIR = CWD + "/tests/test-configs/extractors"
MOCKHOSTDATA = CWD + "/tests/test-configs/mockhostdata/mockhost.json"
MOCK_XTRCTR_DETAILS=["input_id_string", '"samplehost_title"', ["xtrctr_samplehost.json"]]
with open(MOCKHOSTDATA, "r", encoding="utf-8") as file:
    dict_config = json.load(file)

def test_create_extractor_success_not_existing(mocker,capsys) -> None:
    """Function:test_create_extractor_success_not_existing"""
    mock_response = mock_get_response(201,{"extractor_id":"new_extractor_id"})
    mocker.patch('src.setup.gen_list_host_config_sets',return_value=dict_config)
    mocker.patch('src.setup.gen_list_extractor_details',return_value=MOCK_XTRCTR_DETAILS)
    mocker.patch('src.setup.check_extractor_exists',return_value=["xtrctr_title"])
    mocker.patch('requests.post', return_value=mock_response)
    create_extractors(BOOL_VERBOSE_TRUE,XTRCTRCONFIGDIR,HOSTCONFIGDIR,MOCK_STR_INPUTS_URL,
                      MOCK_DICT_GET_HEADERS,MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing extractors\n"
        "  1 Extractor config files to process.\n"
        "     Creating extractor: ['xtrctr_title'] for input \"samplehost_title\"\n"
        "    Extractor added: {'extractor_id': 'new_extractor_id'}\n"
        "[Done] processing extractors.\n\n"
    )
    assert captured.out == expected_output

def test_create_extractor_fail_non_201(mocker,capsys) -> None:
    """Function:test_create_extractor_fail_non_201"""
    mock_response = mock_get_response(400,"Create extractor failure")
    mocker.patch('src.setup.gen_list_host_config_sets',return_value=dict_config)
    mocker.patch('src.setup.gen_list_extractor_details',return_value=MOCK_XTRCTR_DETAILS)
    mocker.patch('src.setup.check_extractor_exists',return_value=["xtrctr_title"])
    mocker.patch('requests.post', return_value=mock_response)
    with pytest.raises(SystemExit) as e:
        create_extractors(BOOL_VERBOSE_TRUE,XTRCTRCONFIGDIR,HOSTCONFIGDIR,
            MOCK_STR_INPUTS_URL,MOCK_DICT_GET_HEADERS,MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing extractors\n"
        "  1 Extractor config files to process.\n"
        "     Creating extractor: ['xtrctr_title'] for input \"samplehost_title\"\n"
        "[ERROR] Add extractor failed. Message:Create extractor failure\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_create_extractor_fail_filenotfound(capsys) -> None:
    """Function:test_create_extractor_fail_filenotfound"""
    with pytest.raises(SystemExit) as e:
        create_extractors(BOOL_VERBOSE_TRUE,"bad_path",HOSTCONFIGDIR,
            MOCK_STR_INPUTS_URL,MOCK_DICT_GET_HEADERS,MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    message = "[ERROR] File or directory not found in create_extractors:"
    expected_output = (
        "Processing extractors\n"
        f"{message} [Errno 2] No such file or directory: 'bad_path'\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_create_extractor_fail_request_exception(mocker,capsys) -> None:
    """Function:test_create_extractor_fail_request_exception"""
    mocker.patch('src.setup.gen_list_host_config_sets',return_value=dict_config)
    mocker.patch('src.setup.gen_list_extractor_details',return_value=MOCK_XTRCTR_DETAILS)
    mocker.patch('src.setup.check_extractor_exists',return_value=["xtrctr_title"])
    mocker.patch('requests.post', side_effect=requests.exceptions.RequestException("Connection error"))
    with pytest.raises(SystemExit) as e:
        create_extractors(BOOL_VERBOSE_TRUE,XTRCTRCONFIGDIR,HOSTCONFIGDIR,
            MOCK_STR_INPUTS_URL,MOCK_DICT_GET_HEADERS,MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing extractors\n"
        "  1 Extractor config files to process.\n"
        "     Creating extractor: ['xtrctr_title'] for input \"samplehost_title\"\n"
        "[ERROR] Request error in create_extractors: Connection error\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_create_extractor_fail_json_decode(mocker,capsys) -> None:
    """Function:test_create_extractor_fail_json_decode"""
    xtrctrconfigdir = CWD + "/tests/test-configs/badconfig"
    mocker.patch('src.setup.gen_list_host_config_sets',return_value=dict_config)
    mocker.patch('src.setup.gen_list_extractor_details',return_value=MOCK_XTRCTR_DETAILS)
    mocker.patch('src.setup.check_extractor_exists',return_value=["xtrctr_title"])
    with pytest.raises(SystemExit) as e:
        create_extractors(BOOL_VERBOSE_TRUE,xtrctrconfigdir,HOSTCONFIGDIR,
            MOCK_STR_INPUTS_URL,MOCK_DICT_GET_HEADERS,MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    message = "[ERROR] There was a problem decoding json in create_extractors:"
    expected_output = (
        "Processing extractors\n"
        "  1 Extractor config files to process.\n"
        f"     Creating extractor: ['xtrctr_title'] for input \"samplehost_title\"\n"
        f"{message} Expecting value: line 1 column 1 (char 0)\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
