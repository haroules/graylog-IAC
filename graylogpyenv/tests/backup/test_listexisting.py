""" backup test_listexisting module"""
import os
from pathlib import Path
import pytest
from src.backup import list_existing_backups

def create_sample_config_dir(base_dir: Path, name: str, file_count: int = 2) -> Path:
    """backup create_sample_config_dir function"""
    config_dir = base_dir / name
    config_dir.mkdir()
    for i in range(file_count):
        file_path = config_dir / f"config_{i}.txt"
        file_path.write_text(f"This is file {i}")
    return config_dir

def test_list_existing_backups_pass_mocked_filesystem(tmp_path) -> None:
    """backup test_list_existing_backups_pass_mocked_filesystem function"""
    create_sample_config_dir(tmp_path, "backup-A")
    create_sample_config_dir(tmp_path, "backup-B")
    create_sample_config_dir(tmp_path, "backup-C")
    result = list_existing_backups(tmp_path)
    assert result == 3

def test_list_existing_backups_fail_filenotfound(capsys) -> None:
    """backup test_list_existing_backups_fail_filenotfound function"""
    message = "FileNotFoundError in list_existing_backups [Errno 2] No such file or directory"
    mock_bad_path = "bad-path"
    with pytest.raises(SystemExit):
        with pytest.raises(FileNotFoundError):
            list_existing_backups(mock_bad_path)
    captured = capsys.readouterr()
    assert captured.out == f"[ERROR] {message}: '{mock_bad_path}'\n"

def test_list_existing_backups_fail_raised_oserror(capsys) -> None:
    """backup test_list_existing_backups_fail_raised_oserror function"""
    mock_bad_dir = True
    with pytest.raises(SystemExit):
        with pytest.raises(os.error):
            list_existing_backups(mock_bad_dir)
    captured = capsys.readouterr()
    assert captured.out == f"[ERROR] An OSError occurred in list_existing_backups [Errno 20] Not a directory: {mock_bad_dir}\n"
