"""tests.setup test_gen_list_host_config_files module"""
import pytest

from tests.setup.test_setup_common import create_sample_host_config_dir
from src.setup import gen_list_host_config_files
MOCK_BOOL_VERBOSE=True
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
        "stream_config_file":"config_0.json",
        "stream_title":"samplehost_stream"
        }]

def test_gen_list_host_config_files_success(tmp_path,capsys) -> None:
    """tests.setup test_create_extractor_success_not_existing function"""
    hostconfig=create_sample_host_config_dir(tmp_path,"config-1")
    hostconfigfile_path = tmp_path.as_posix()+"/config-1/config_0.json"
    return_value = gen_list_host_config_files(MOCK_BOOL_VERBOSE,hostconfig)
    captured = capsys.readouterr()
    expected_output = (
        f"  Adding host config to list:{hostconfigfile_path}\n"
    )
    assert captured.out == expected_output
    assert return_value == [hostconfigfile_path]

def test_gen_list_host_config_files_fail_oserrror(capsys) -> None:
    """tests.setup test_create_extractor_success_not_existing function"""
    with pytest.raises(SystemExit) as e:
        gen_list_host_config_files(MOCK_BOOL_VERBOSE,"bad_path")
    captured = capsys.readouterr()
    message = "[ERROR] An OSError occurred in gen_list_host_config_files:"
    expected_output = (
       f"{message} [Errno 2] No such file or directory: 'bad_path'\n"
    )
    assert captured.out == expected_output
    assert e.value.code == 1
