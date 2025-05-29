"""tests.setup test_create_extractors module"""
from unittest.mock import Mock
import requests
import pytest

from src.setup import create_extractors
from tests.setup.test_setup_common import create_sample_extractor_config_dir
from tests.setup.test_setup_common import create_bad_sample_extractor_config_dir
from tests.setup.test_setup_common import create_sample_host_config_dir

MOCK_BOOL_VEBOSE=True
MOCK_INPUTS_URL="https://mock.api/inputs"
MOCK_DICT_GET_HEADERS={"Authorization": "Bearer mock"}
MOCK_DICT_POST_HEADERS={"Authorization": "Bearer mock"}
MOCK_HOST_CONFIG=[{
        "index_config_file":"index_samplehost.json",
        "index_title":"samplehost_title",
        "input_config_file":"input_samplehost.json",
        "input_title":"samplehost_title",
        "extractors_total":1,
        "extractors":[{
            "extractor_config_file" :"config_0.json",
            "extractor_title" : "some_extractor"
        }],
        "stream_config_file":"<replace>",
        "stream_title":"<replace>"
        }]
MOCK_XTRCTR_DETAILS=["input_id_string", '"samplehost_title"', ["config_0.json"]]

def test_create_extractor_success_not_existing(tmp_path,mocker,capsys) -> None:
    """tests.setup test_create_extractor_success_not_existing function"""
    create_sample_extractor_config_dir(tmp_path,"config-1")
    xtrctrconfig_path=tmp_path.as_posix()+"/config-1"
    hostconfig=create_sample_host_config_dir(tmp_path,"config-2")
    mock_response = Mock()
    mock_response.status_code = 201
    mock_response.text = {"extractor_id":"new_extractor_id"}
    mock_response.raise_for_status = Mock()
    mocker.patch('src.setup.gen_list_host_config_sets',return_value=MOCK_HOST_CONFIG)
    mocker.patch('src.setup.gen_list_extractor_details',return_value=MOCK_XTRCTR_DETAILS)
    mocker.patch('src.setup.check_extractor_exists',return_value=["xtrctr_title"])
    mocker.patch('requests.post', return_value=mock_response)
    create_extractors(MOCK_BOOL_VEBOSE,xtrctrconfig_path,hostconfig,MOCK_INPUTS_URL,MOCK_DICT_GET_HEADERS,MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing extractors\n"
        "  1 Extractor config files to process.\n"
        "     Creating extractor: ['xtrctr_title'] for input \"samplehost_title\"\n"
        "    Extractor added: {'extractor_id': 'new_extractor_id'}\n"
        "[Done] processing extractors.\n\n"
    )
    assert captured.out == expected_output

def test_create_extractor_fail_non_201(tmp_path,mocker,capsys) -> None:
    """tests.setup test_create_extractor_fail_non_201 module"""
    create_sample_extractor_config_dir(tmp_path,"config-1")
    xtrctrconfig_path=tmp_path.as_posix()+"/config-1"
    hostconfig=create_sample_host_config_dir(tmp_path,"config-2")
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Create extractor failure"
    mock_response.raise_for_status = Mock()
    mocker.patch('src.setup.gen_list_host_config_sets',return_value=MOCK_HOST_CONFIG)
    mocker.patch('src.setup.gen_list_extractor_details',return_value=MOCK_XTRCTR_DETAILS)
    mocker.patch('src.setup.check_extractor_exists',return_value=["xtrctr_title"])
    mocker.patch('requests.post', return_value=mock_response)
    with pytest.raises(SystemExit) as e:
        create_extractors(MOCK_BOOL_VEBOSE,xtrctrconfig_path,hostconfig,
            MOCK_INPUTS_URL,MOCK_DICT_GET_HEADERS,MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing extractors\n"
        "  1 Extractor config files to process.\n"
        "     Creating extractor: ['xtrctr_title'] for input \"samplehost_title\"\n"
        "[ERROR] Add extractor failed. Message:Create extractor failure\n"
    )
    assert captured.out == expected_output
    assert e.value.code == 1

def test_create_extractor_fail_filenotfound(tmp_path,capsys) -> None:
    """tests.setup test_create_extractor_fail_filenotfound"""
    create_sample_extractor_config_dir(tmp_path,"config-1")
    xtrctrconfig_path=tmp_path.as_posix()+"/config-0"
    hostconfig=create_sample_host_config_dir(tmp_path,"config-2")
    with pytest.raises(SystemExit) as e:
        create_extractors(MOCK_BOOL_VEBOSE,xtrctrconfig_path,hostconfig,
            MOCK_INPUTS_URL,MOCK_DICT_GET_HEADERS,MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    message = "[ERROR] File or directory not found in create_extractors:"
    expected_output = (
        "Processing extractors\n"
        f"{message} [Errno 2] No such file or directory: '{xtrctrconfig_path}'\n"
    )
    assert captured.out == expected_output
    assert e.value.code == 1

def test_create_extractor_fail_request_exception(tmp_path,mocker,capsys) -> None:
    """tests.setup test_create_extractor_fail_request_exception function"""
    create_sample_extractor_config_dir(tmp_path,"config-1")
    xtrctrconfig_path=tmp_path.as_posix()+"/config-1"
    hostconfig=create_sample_host_config_dir(tmp_path,"config-2")
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "request exception"
    mock_response.raise_for_status = Mock()
    mocker.patch('src.setup.gen_list_host_config_sets',return_value=MOCK_HOST_CONFIG)
    mocker.patch('src.setup.gen_list_extractor_details',return_value=MOCK_XTRCTR_DETAILS)
    mocker.patch('src.setup.check_extractor_exists',return_value=["xtrctr_title"])
    mocker.patch('requests.post', side_effect=requests.exceptions.RequestException("Connection error"))
    with pytest.raises(SystemExit) as e:
        create_extractors(MOCK_BOOL_VEBOSE,xtrctrconfig_path,hostconfig,
            MOCK_INPUTS_URL,MOCK_DICT_GET_HEADERS,MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "Processing extractors\n"
        "  1 Extractor config files to process.\n"
        "     Creating extractor: ['xtrctr_title'] for input \"samplehost_title\"\n"
        "[ERROR] Request error in create_extractors: Connection error\n"
    )
    assert captured.out == expected_output
    assert e.value.code == 1

def test_create_extractor_fail_json_decode(tmp_path,mocker,capsys) -> None:
    """tests.setup test_create_extractor_fail_json_decode function"""
    create_bad_sample_extractor_config_dir(tmp_path,"config-1")
    xtrctrconfig_path=tmp_path.as_posix()+"/config-1"
    hostconfig=create_sample_host_config_dir(tmp_path,"config-2")
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "bad json"
    mock_response.raise_for_status = Mock()
    mocker.patch('src.setup.gen_list_host_config_sets',return_value=MOCK_HOST_CONFIG)
    mocker.patch('src.setup.gen_list_extractor_details',return_value=MOCK_XTRCTR_DETAILS)
    mocker.patch('src.setup.check_extractor_exists',return_value=["xtrctr_title"])
    with pytest.raises(SystemExit) as e:
        create_extractors(MOCK_BOOL_VEBOSE,xtrctrconfig_path,hostconfig,
            MOCK_INPUTS_URL,MOCK_DICT_GET_HEADERS,MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    message = "[ERROR] There was a problem decoding json in create_extractors:"
    expected_output = (
        "Processing extractors\n"
        "  1 Extractor config files to process.\n"
        f"     Creating extractor: ['xtrctr_title'] for input \"samplehost_title\"\n"
        f"{message} Expecting value: line 1 column 1 (char 0)\n"
    )
    assert captured.out == expected_output
    assert e.value.code == 1
