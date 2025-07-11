"""Module:tests.backup.test_copydirectories"""
import os
import shutil
from unittest import mock
import pytest

from src.backup import copy_directories
from tests.common.test_common import create_config_dir
from tests.common.test_common import folder_asserts
from tests.common.test_common import shared_asserts
from tests.common.test_common import BOOL_VERBOSE_TRUE
from tests.common.test_common import BOOL_VERBOSE_FALSE

DIRECTORIES = ['/mock/source']
DEST_BASE = '/mock/destination'

def test_copy_directories_pass(tmp_path, capsys) -> None:
    """Function:test_copy_directories_pass"""
    config1 = create_config_dir(tmp_path, "configA")
    config2 = create_config_dir(tmp_path, "configB")
    backup_base = tmp_path / "graylogbackup" / "configs"
    args = [config1.as_posix(), config2.as_posix()]
    backup_base.mkdir(parents=True)
    copy_directories(args, backup_base, BOOL_VERBOSE_TRUE)
    captured = capsys.readouterr()
    expected_output = (
        f"  Copied '{tmp_path}/configA' to '{tmp_path}/graylogbackup/configs/configA'\n"
        f"  Copied '{tmp_path}/configB' to '{tmp_path}/graylogbackup/configs/configB'\n"
    )
    assert captured.out == expected_output
    folder_asserts(backup_base)

def test_copy_directories_fail_oserror(monkeypatch, capsys) -> None:
    """Function:test_copy_directories_fail_oserror"""
    mock_os_error = "Mocked OS error"
    monkeypatch.setattr(os.path, 'basename', lambda path: 'source')
    monkeypatch.setattr(shutil, 'copytree', mock.Mock(side_effect=OSError(mock_os_error)))
    with pytest.raises(SystemExit) as e:
        copy_directories(DIRECTORIES, DEST_BASE, BOOL_VERBOSE_FALSE)
    captured = capsys.readouterr()
    expected_output = f"[ERROR]: An OSError occurred in copy_directories: {mock_os_error}\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_copy_directories_fail_shutilsamefileerror(monkeypatch,capsys) -> None:
    """Function:test_copy_directories_fail_shutilsamefileerror"""
    mock_same_file_error = "same file error"
    monkeypatch.setattr(os.path, 'basename', lambda path: 'source')
    monkeypatch.setattr(shutil, 'copytree', mock.Mock(side_effect=shutil.SameFileError(mock_same_file_error)))
    with pytest.raises(SystemExit) as e:
        copy_directories(DIRECTORIES, DEST_BASE, BOOL_VERBOSE_FALSE)
    captured = capsys.readouterr()
    expected_output = f"[ERROR]: An OSError occurred in copy_directories: {mock_same_file_error}\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_copy_directories_fail_shutilerror(monkeypatch,capsys) -> None:
    """Function:test_copy_directories_fail_shutilerror"""
    mock_shutil_error = "generic shutil error"
    monkeypatch.setattr(os.path, 'basename', lambda path: 'source')
    monkeypatch.setattr(shutil, 'copytree', mock.Mock(side_effect=shutil.Error(mock_shutil_error)))
    with pytest.raises(SystemExit) as e:
        copy_directories(DIRECTORIES, DEST_BASE, BOOL_VERBOSE_FALSE)
    captured = capsys.readouterr()
    expected_output = f"[ERROR]: An OSError occurred in copy_directories: {mock_shutil_error}\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
