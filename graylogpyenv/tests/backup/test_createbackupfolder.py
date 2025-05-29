"""backup test_create_backup_folder module"""
import os
import shutil
from unittest.mock import patch
import pytest
from src.backup import create_backup_folder

VALID_CWD = os.path.dirname(os.getcwd())
VALID_MOCK_TIMESTAMP = "04-19-2025-010000"
VALID_MONKEYPATCH_DATETIMENOW = "20250419-010000"

def test_create_backup_folder_fail_patched_oserror(capsys) -> None:
    """backup test_create_backup_folder_fail_patched_oserror function"""
    mocked_oserror = "Mocked OSError"
    with patch('os.makedirs', side_effect=OSError(mocked_oserror)):
        with pytest.raises(SystemExit) as e:
            with pytest.raises(OSError):
                create_backup_folder("bad_path",VALID_MOCK_TIMESTAMP, False)
        captured = capsys.readouterr()
        assert captured.out == f"[ERROR] An OSError occurred in create_backup_folder: {mocked_oserror}\n"
        assert e.value.code == 1

def test_create_backup_folder_fail_patched_fileexists_error(capsys) -> None:
    """backup test_create_backup_folder_fail_patched_fileexists_error function"""
    mocked_exists_error = "Mocked File Exists Error"
    with patch('os.makedirs', side_effect=FileExistsError(mocked_exists_error)):
        with pytest.raises(SystemExit) as e:
            with pytest.raises(FileExistsError):
                badpath_arg = "bad_path"
                create_backup_folder(badpath_arg,VALID_MOCK_TIMESTAMP, False)
        captured = capsys.readouterr()
        assert captured.out == f"[ERROR] FileExistsError in create_backup_folder {mocked_exists_error}\n"
        assert e.value.code == 1

def test_create_backup_folder_fail_patched_filenotfound_error(capsys) -> None:
    """backup test_create_backup_folder_fail_patched_filenotfound_error function"""
    mocked_notfound_error = "Mocked FileNotFound Error"
    with patch('os.makedirs', side_effect=FileNotFoundError(mocked_notfound_error)):
        with pytest.raises(SystemExit) as e:
            with pytest.raises(FileNotFoundError):
                badpath_arg = "bad_path"
                create_backup_folder(badpath_arg,VALID_MOCK_TIMESTAMP, False)
        captured = capsys.readouterr()
        assert captured.out == f"[ERROR] FileNotFoundError in create_backup_folder {mocked_notfound_error}\n"
        assert e.value.code == 1

def test_create_backup_folder_pass_nonverbose(capsys, monkeypatch) -> None:
    """backup test_create_backup_folder_pass_nonverbose function"""
    test_backup_dir = VALID_CWD + "/backup-" + VALID_MOCK_TIMESTAMP
    monkeypatch.setattr("src.backup.generate_timestamp", lambda: VALID_MONKEYPATCH_DATETIMENOW)
    create_backup_folder(VALID_CWD,VALID_MOCK_TIMESTAMP, False)
    captured = capsys.readouterr()
    assert captured.out == ""
    if os.path.exists(test_backup_dir):
        shutil.rmtree(test_backup_dir) # remove directory created by test before and after test

def test_create_backup_folder_pass_verbose(capsys, monkeypatch) -> None:
    """backup test_create_backup_folder_pass_verbose function"""
    test_backup_dir = VALID_CWD + "/backup-" + VALID_MOCK_TIMESTAMP
    monkeypatch.setattr("src.backup.generate_timestamp", lambda: VALID_MONKEYPATCH_DATETIMENOW)
    create_backup_folder(VALID_CWD,VALID_MOCK_TIMESTAMP, True)
    captured = capsys.readouterr()
    assert captured.out == f"  Creating backup directory: '{test_backup_dir}'\n"
    if os.path.exists(test_backup_dir):
        shutil.rmtree(test_backup_dir) # remove directory created by test before and after test
