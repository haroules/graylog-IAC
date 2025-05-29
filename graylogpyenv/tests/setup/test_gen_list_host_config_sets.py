"""tests.setup test_gen_list_host_config_sets module"""
import pytest

from src.setup import gen_list_host_config_sets
from tests.setup.test_setup_common import create_sample_host_config_dir
from tests.setup.test_setup_common import create_bad_sample_host_config_dir

MOCK_BOOL_VEBOSE=True
MOCK_RETURN_VAL=[{
        "index_config_file":"index_samplehost.json",
        "index_title":"samplehost_title",
        "input_config_file":"input_samplehost.json",
        "input_title":"samplehost_title",
        "extractors_total":1,
        "extractors":[{
            "extractor_config_file" :"extractor.json",
            "extractor_title" : "some_extractor"
        }],
        "stream_config_file":"config_0.json",
        "stream_title":"samplehost_stream"
        }]

def test_gen_list_host_config_sets_verbose_success(tmp_path,capsys) -> None:
    """setup test_gen_list_host_config_sets_non_verbose_success function"""
    config=create_sample_host_config_dir(tmp_path,"config-1")
    path_config_file = tmp_path.as_posix()+"/config-1/config_0.json"
    return_val=gen_list_host_config_sets(MOCK_BOOL_VEBOSE,config,path_config_file)
    captured = capsys.readouterr()
    assert captured.out == f"  {path_config_file} has 1 extractors defined\n"
    assert return_val == MOCK_RETURN_VAL

def test_gen_list_host_config_sets_fail_filenotfound(tmp_path,capsys) -> None:
    """setup test_gen_list_host_config_sets_fail_filenotfound function"""
    config=create_sample_host_config_dir(tmp_path,"config-1")
    with pytest.raises(SystemExit) as e:
        gen_list_host_config_sets(MOCK_BOOL_VEBOSE,config,"bad_file_path")
    captured = capsys.readouterr()
    message = "[ERROR]: File or directory not found in gen_list_host_config_sets:"
    expected_output = (
        f"{message} [Errno 2] No such file or directory: '{config}/bad_file_path'\n"
    )
    assert captured.out == expected_output
    assert e.value.code == 1

def test_gen_list_host_config_sets_fail_json_decode(tmp_path,capsys) -> None:
    """setup test_gen_list_host_config_sets_fail_json_decode function"""
    config=create_bad_sample_host_config_dir(tmp_path,"config-1")
    path_config_file = tmp_path.as_posix()+"/config-1/config_0.json"
    with pytest.raises(SystemExit) as e:
        gen_list_host_config_sets(MOCK_BOOL_VEBOSE,config,path_config_file)
    captured = capsys.readouterr()
    message = "[ERROR] There was a problem decoding json in gen_list_host_config_sets:"
    expected_output = (
        f"{message} Expecting value: line 1 column 1 (char 0)\n"
    )
    assert captured.out == expected_output
    assert e.value.code == 1
