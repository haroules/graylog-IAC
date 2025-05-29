"""setup test_get_list_index_config_files module"""
import pytest

from src.setup import get_list_config_files
from tests.setup.test_setup_common import create_sample_index_config_dir
from tests.setup.test_setup_common import create_empty_index_config_dir

def test_get_list_index_config_files_non_verbose_success(tmp_path) -> None:
    """setup test_get_list_config_files_non_verbose_success function"""
    config=create_sample_index_config_dir(tmp_path,"config-1")
    result = get_list_config_files(False,config,"index")
    assert isinstance(result, list)
    assert tmp_path.as_posix()+"/config-1/config_0.json" in result
    assert tmp_path.as_posix()+"/config-1/config_1.json" in result

def test_get_list_config_files_verbose_success(tmp_path,capsys) -> None:
    """setup test_get_list_config_files_verbose_success function"""
    config=create_sample_index_config_dir(tmp_path,"config-1")
    result = get_list_config_files(True, config,"index")
    captured = capsys.readouterr()
    assert isinstance(result, list)
    assert tmp_path.as_posix()+"/config-1/config_0.json" in result
    assert tmp_path.as_posix()+"/config-1/config_1.json" in result
    assert captured.out == "  2 index config files to process.\n"

def test_get_list_config_files_fail_noconfigfiles(tmp_path,capsys) -> None:
    """setup test_get_list_config_files_fail_noconfigfiles function"""
    config=create_empty_index_config_dir(tmp_path,"config-1")
    with pytest.raises(SystemExit) as e:
        get_list_config_files(True, config,"index")
    captured = capsys.readouterr()
    assert captured.out == "[ERROR] No config files found for creating index. Exiting.\n"
    assert e.value.code == 1

def test_get_list_config_files_fail_oserror(capsys) -> None:
    """setup test_get_list_index_config_files_fail_oserror function"""
    with pytest.raises(SystemExit) as e:
        get_list_config_files(False, "bad-path","index")
    captured = capsys.readouterr()
    message = "[ERROR] An OSError occurred getting list of index config files."
    assert captured.out == f"{message} Error was: [Errno 2] No such file or directory: 'bad-path'\n"
    assert e.value.code == 1
