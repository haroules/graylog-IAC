"""Module:tests.backup.test_create_backup_folder"""
import os
import shutil
from unittest.mock import patch
import pytest

from src.backup import create_backup_folder
from tests.common.test_common import shared_asserts
from tests.common.test_common import BOOL_VERBOSE_TRUE
from tests.common.test_common import BOOL_VERBOSE_FALSE

CWD = os.path.dirname(os.getcwd())
MOCK_TIMESTAMP = "04-19-2025-010000"
MOCK_DATETIMENOW = "20250419-010000"

def test_create_backup_folder_fail_oserror(capsys) -> None:
    """Function:test_create_backup_folder_fail_oserror"""
    mocked_oserror = "Mocked OSError"
    with patch('os.makedirs', side_effect=OSError(mocked_oserror)):
        with pytest.raises(SystemExit) as e:
            with pytest.raises(OSError):
                create_backup_folder("bad_path",MOCK_TIMESTAMP, BOOL_VERBOSE_FALSE)
        captured = capsys.readouterr()
        expected_output = f"[ERROR] An OSError occurred in create_backup_folder: {mocked_oserror}\n"
        shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_create_backup_folder_fail_filexists_error(capsys) -> None:
    """Function:test_create_backup_folder_fail_filexists_error"""
    mocked_exists_error = "Mocked File Exists Error"
    with patch('os.makedirs', side_effect=FileExistsError(mocked_exists_error)):
        with pytest.raises(SystemExit) as e:
            with pytest.raises(FileExistsError):
                badpath_arg = "bad_path"
                create_backup_folder(badpath_arg,MOCK_TIMESTAMP, BOOL_VERBOSE_FALSE)
        captured = capsys.readouterr()
        expected_output = f"[ERROR] FileExistsError in create_backup_folder {mocked_exists_error}\n"
        shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_create_backup_folder_fail_filenotfound_error(capsys) -> None:
    """Function:test_create_backup_folder_fail_filenotfound_error"""
    mocked_notfound_error = "Mocked FileNotFound Error"
    with patch('os.makedirs', side_effect=FileNotFoundError(mocked_notfound_error)):
        with pytest.raises(SystemExit) as e:
            with pytest.raises(FileNotFoundError):
                badpath_arg = "bad_path"
                create_backup_folder(badpath_arg,MOCK_TIMESTAMP, BOOL_VERBOSE_FALSE)
        captured = capsys.readouterr()
        expected_output = f"[ERROR] FileNotFoundError in create_backup_folder {mocked_notfound_error}\n"
        shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_create_backup_folder_pass_verbose(capsys, monkeypatch) -> None:
    """Function:test_create_backup_folder_pass_verbose"""
    test_backup_dir = CWD + "/backup-" + MOCK_TIMESTAMP
    monkeypatch.setattr("src.backup.generate_timestamp", lambda: MOCK_DATETIMENOW)
    create_backup_folder(CWD,MOCK_TIMESTAMP, BOOL_VERBOSE_TRUE)
    captured = capsys.readouterr()
    assert captured.out == f"  Creating backup directory: '{test_backup_dir}'\n"
    if os.path.exists(test_backup_dir):
        shutil.rmtree(test_backup_dir) # remove directory created by test
