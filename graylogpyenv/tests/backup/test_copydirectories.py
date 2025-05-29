"""tests.backup test_copydirectories module"""
import os
import shutil
from unittest import mock
import pytest
from src.backup import copy_directories
from tests.backup.test_backup_common import create_sample_config_dir

def test_copy_directories_pass_nonverbose(tmp_path) -> None:
    """tests.backup test_copy_directories_pass_nonverbose function"""
    # Setup fake config dirs with files
    config1 = create_sample_config_dir(tmp_path, "configA")
    config2 = create_sample_config_dir(tmp_path, "configB")
    # Where the backup should go
    backup_base = tmp_path / "graylogbackup" / "configs"
    args = [config1.as_posix(), config2.as_posix()]
    backup_base.mkdir(parents=True)
    copy_directories(args, backup_base, False)
    # Check if backup folder was created
    assert backup_base.exists()
    assert backup_base.is_dir()
    # Check if directories and files are copied
    copied_configa = backup_base / "configA"
    copied_configb = backup_base / "configB"
    assert copied_configa.exists()
    assert copied_configb.exists()
    for i in range(2):
        assert (copied_configa / f"config_{i}.txt").read_text() == f"This is file {i}"
        assert (copied_configb / f"config_{i}.txt").read_text() == f"This is file {i}"

def test_copy_directories_pass_verbose(tmp_path, capsys):
    """Function test_copy_directories_pass_verbose"""
    # Setup fake config dirs with files
    config1 = create_sample_config_dir(tmp_path, "configA")
    config2 = create_sample_config_dir(tmp_path, "configB")
    # Where the backup should go
    backup_base = tmp_path / "graylogbackup" / "configs"
    args = [config1.as_posix(), config2.as_posix()]
    backup_base.mkdir(parents=True)
    copy_directories(args, backup_base, True)
    captured = capsys.readouterr()
    expected_output = (
        f"  Copied '{tmp_path}/configA' to '{tmp_path}/graylogbackup/configs/configA'\n"
        f"  Copied '{tmp_path}/configB' to '{tmp_path}/graylogbackup/configs/configB'\n"
    )
    assert captured.out == expected_output
    # Check if backup folder was created
    assert backup_base.exists()
    assert backup_base.is_dir()
    # Check if directories and files are copied
    copied_configa = backup_base / "configA"
    copied_configb = backup_base / "configB"
    assert copied_configa.exists()
    assert copied_configb.exists()
    for i in range(2):
        assert (copied_configa / f"config_{i}.txt").read_text() == f"This is file {i}"
        assert (copied_configb / f"config_{i}.txt").read_text() == f"This is file {i}"

def test_copy_directories_fail_raised_oserror(monkeypatch, capsys):
    """Function test_copy_directories_fail_raised_oserror"""
    mock_os_error = "Mocked OS error"
    directories = ['/mock/source']
    dest_base = '/mock/destination'
    monkeypatch.setattr(os.path, 'basename', lambda path: 'source')
    monkeypatch.setattr(shutil, 'copytree', mock.Mock(side_effect=OSError(mock_os_error)))
    with pytest.raises(SystemExit) as e:
        copy_directories(directories, dest_base, bool_verbose=False)
    captured = capsys.readouterr()
    assert captured.out == f"[ERROR]: An OSError occurred in copy_directories: {mock_os_error}\n"
    assert e.type == SystemExit
    assert e.value.code == 1

def test_copy_directories_fail_raised_shutilsamefileerror(monkeypatch,capsys):
    """Function test_copy_directories_fail_raised_shutilsamefileerror"""
    mock_same_file_error = "same file error"
    directories = ['/mock/source']
    dest_base = '/mock/destination'
    monkeypatch.setattr(os.path, 'basename', lambda path: 'source')
    monkeypatch.setattr(shutil, 'copytree', mock.Mock(side_effect=shutil.SameFileError(mock_same_file_error)))
    with pytest.raises(SystemExit) as e:
        copy_directories(directories, dest_base, bool_verbose=False)
    captured = capsys.readouterr()
    assert captured.out == f"[ERROR]: An OSError occurred in copy_directories: {mock_same_file_error}\n"
    assert e.type == SystemExit
    assert e.value.code == 1

def test_copy_directories_fail_raised_shutilerror(monkeypatch,capsys):
    """Function test_copy_directories_fail_raised_shutilerror"""
    mock_shutil_error = "generic shutil error"
    directories = ['/mock/source']
    dest_base = '/mock/destination'
    monkeypatch.setattr(os.path, 'basename', lambda path: 'source')
    monkeypatch.setattr(shutil, 'copytree', mock.Mock(side_effect=shutil.Error(mock_shutil_error)))
    with pytest.raises(SystemExit) as e:
        copy_directories(directories, dest_base, bool_verbose=False)
    captured = capsys.readouterr()
    assert captured.out == f"[ERROR]: An OSError occurred in copy_directories: {mock_shutil_error}\n"
    assert e.type == SystemExit
    assert e.value.code == 1
