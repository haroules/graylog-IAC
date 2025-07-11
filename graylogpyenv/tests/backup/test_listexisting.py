"""Module:tests.backup.test_listexisting"""
import os
import pytest

from src.backup import list_existing_backups
from tests.common.test_common import create_config_dir
from tests.common.test_common import shared_asserts

def test_list_existing_backups_pass(tmp_path) -> None:
    """Function:test_list_existing_backups_pass"""
    create_config_dir(tmp_path, "backup-A")
    create_config_dir(tmp_path, "backup-B")
    create_config_dir(tmp_path, "backup-C")
    result = list_existing_backups(tmp_path)
    assert result == 3

def test_list_existing_backups_fail_filenotfound(capsys) -> None:
    """Function:test_list_existing_backups_fail_filenotfound"""
    message = "FileNotFoundError in list_existing_backups [Errno 2] No such file or directory"
    mock_bad_path = "bad-path"
    with pytest.raises(SystemExit) as e:
        with pytest.raises(FileNotFoundError):
            list_existing_backups(mock_bad_path)
    captured = capsys.readouterr()
    expected_output = f"[ERROR] {message}: '{mock_bad_path}'\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_list_existing_backups_fail_oserror(capsys) -> None:
    """Function:test_list_existing_backups_fail_oserror"""
    mock_bad_dir = True
    with pytest.raises(SystemExit) as e:
        with pytest.raises(os.error):
            list_existing_backups(mock_bad_dir)
    captured = capsys.readouterr()
    expected_output = f"[ERROR] An OSError occurred in list_existing_backups [Errno 20] Not a directory: {mock_bad_dir}\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
