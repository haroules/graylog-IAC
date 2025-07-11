"""Module:tests.setup.test_get_list_index_config_files"""
import os
import pytest

from src.setup import get_list_config_files
from tests.common.test_common import create_empty_config_dir
from tests.common.test_common import shared_asserts

CWD = os.getcwd()
INDEXCONFIGDIR = CWD + "/tests/test-configs/indices"
INDEXCONFIGFILE = CWD + "/tests/test-configs/indices/index_samplehost.json"

def test_get_list_index_config_files_non_verbose_success() -> None:
    """Function:test_get_list_index_config_files_non_verbose_success"""
    result = get_list_config_files(False,INDEXCONFIGDIR,"index")
    assert isinstance(result, list)
    assert INDEXCONFIGFILE in result

def test_get_list_config_files_verbose_success(capsys) -> None:
    """Function:test_get_list_config_files_verbose_success"""
    result = get_list_config_files(True, INDEXCONFIGDIR,"index")
    captured = capsys.readouterr()
    assert isinstance(result, list)
    assert INDEXCONFIGFILE in result
    assert captured.out == "  1 index config files to process.\n"

def test_get_list_config_files_fail_noconfigfiles(tmp_path,capsys) -> None:
    """Function:test_get_list_config_files_fail_noconfigfiles"""
    config=create_empty_config_dir(tmp_path,"config-1")
    with pytest.raises(SystemExit) as e:
        get_list_config_files(True, config,"index")
    captured = capsys.readouterr()
    expected_output = "[ERROR] No config files found for creating index. Exiting.\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_get_list_config_files_fail_oserror(capsys) -> None:
    """Function:test_get_list_config_files_fail_oserror"""
    with pytest.raises(SystemExit) as e:
        get_list_config_files(False, "bad-path","index")
    captured = capsys.readouterr()
    message = "[ERROR] An OSError occurred getting list of index config files."
    expected_output = f"{message} Error was: [Errno 2] No such file or directory: 'bad-path'\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
