"""tests.setup test_gen_list_inputs_to_create module"""

import pytest

from src.setup import gen_list_inputs_to_create
from tests.setup.test_setup_common import create_sample_input_config_dir
from tests.setup.test_setup_common import create_bad_sample_input_config_dir

MOCK_INPUTS_URL="https://mock.api/inputs"
MOCK_DICT_GET_HEADERS={"Authorization": "Bearer mock"}
MOCK_API_RETURN = {"inputs": [ { "title": "input_title_1", "global": True, "name": "input_name_1" } ] }
MOCK_VERBOSE = True
MOCK_JSON_FILE = {"node": "node_id_string", "global": True, "title": "input_title_2"}


def test_gen_list_inputs_to_create_pass_verbose(mocker,tmp_path) -> None:
    """tests.setup test_gen_list_inputs_to_create_pass_verbose function"""
    config = create_sample_input_config_dir(tmp_path, "configA")
    list_configs = [config.as_posix()+ "/config_0.json"]
    mocker.patch('src.setup.gen_list_inputs_titles', return_value=["input_title_1"])
    mocker.patch('json.loads', return_value = [MOCK_JSON_FILE ])
    mocker.patch('src.setup.jq', return_value = ["input_title_2"])
    mocker.patch('src.helpers.contains_sublist', return_value=False)
    return_val = gen_list_inputs_to_create(MOCK_VERBOSE,list_configs,MOCK_INPUTS_URL,MOCK_DICT_GET_HEADERS)
    assert return_val == list_configs

def test_gen_list_inputs_to_create_pass_existing_verbose(mocker,tmp_path,capsys) -> None:
    """tests.setup test_gen_list_inputs_to_create_pass_existing_verbose function"""
    config = create_sample_input_config_dir(tmp_path, "configA")
    list_configs = [config.as_posix()+ "/config_0.json"]
    mocker.patch('src.setup.gen_list_inputs_titles', return_value=["input_title_1"])
    mocker.patch('json.loads', return_value = [MOCK_JSON_FILE ])
    mocker.patch('src.setup.jq', return_value = ["input_title_1"])
    mocker.patch('src.helpers.contains_sublist', return_value=False)
    return_val = gen_list_inputs_to_create(MOCK_VERBOSE,list_configs,MOCK_INPUTS_URL,MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "    input_title_1 Input already exists, skipping creation\n"
    )
    assert captured.out == expected_output
    assert not return_val

def test_gen_list_inputs_to_create_fail_filenotfound(mocker,capsys) -> None:
    """tests.setup test_gen_list_inputs_to_create_fail_filenotfound function"""
    mocker.patch('src.setup.gen_list_inputs_titles', return_value=["input_title_1"])
    with pytest.raises(SystemExit) as e:
        gen_list_inputs_to_create(MOCK_VERBOSE,["bad_path"],MOCK_INPUTS_URL,MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    message = "[ERROR]: File or directory not found in gen_list_inputs_to_create:"
    expected_output = (
        f"{message} [Errno 2] No such file or directory: 'bad_path'\n"
    )
    assert captured.out == expected_output
    assert e.value.code == 1

def test_gen_list_inputs_to_create_fail_json_decode(mocker,tmp_path,capsys) -> None:
    """tests.setup test_gen_list_inputs_to_create_fail_json_decode function"""
    config = create_bad_sample_input_config_dir(tmp_path, "configA")
    list_configs = [config.as_posix()+ "/config_0.json"]
    mocker.patch('src.setup.gen_list_inputs_titles', return_value=["input_title_1"])
    with pytest.raises(SystemExit) as e:
        gen_list_inputs_to_create(MOCK_VERBOSE,list_configs,MOCK_INPUTS_URL,MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    message = "[ERROR] There was a problem decoding json in gen_list_inputs_to_create:"
    expected_output = (
         f"{message} Expecting value: line 1 column 1 (char 0)\n"
    )
    assert captured.out == expected_output
    assert e.value.code == 1
