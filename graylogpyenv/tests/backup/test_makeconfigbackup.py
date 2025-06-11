"""tests.backup test_backup_makeconfigbackup module"""
import os
import shutil
from datetime import datetime
from unittest.mock import patch
import pytest

import global_vars
from src.helpers import set_global_vars
from src.backup import make_config_backup
from src.backup import generate_timestamp
from tests.common.test_common import create_sample_config_dir
from tests.common.test_common import shared_asserts

VALID_SCRIPT = "script.py"
VALID_TOKEN = "TOKEN"
VALID_TEST_URL_NONEXIST = "http://graylog.example.com"
VALID_CWD = os.path.dirname(os.getcwd())
VALID_BOOL_VERBOSE_FALSE = False
VALID_BOOL_VERBOSE_TRUE = True
VALID_MOCK_TIMESTAMP = "04-19-2025-010000"
VALID_MONKEYPATCH_DATETIMENOW = "20250419-010000"
VALID_BACKUP_FOLDERNAME = f"backup-{VALID_MONKEYPATCH_DATETIMENOW}"
FAKE_NOW = datetime(2022, 10, 21, 22, 22, 22).strftime("%m-%d-%Y-%H%M%S")

def test_make_config_backup_verbose_pass_realdata(capsys,mocker) -> None:
    """tests.backup.test_make_config_backup_verbose_pass_valid function"""
    test_backup_dir = VALID_CWD + "/backup-" + VALID_MOCK_TIMESTAMP
     #patch timestamp
    mocker.patch("src.backup.generate_timestamp", return_value=VALID_MOCK_TIMESTAMP)
    #patch list backups to 0 so dont get warning about 5 or more backups
    mocker.patch("src.backup.list_existing_backups", return_value=0)
    args = [VALID_SCRIPT, VALID_TOKEN, VALID_TEST_URL_NONEXIST, VALID_BOOL_VERBOSE_TRUE, VALID_CWD]
    set_global_vars(args) # have to call set global vars, othewise won't have valid global vars
    return_data = make_config_backup(args, global_vars.LIST_CONFIG_DIRECTORIES)
    captured = capsys.readouterr()
    expected_output = (
        "Assigning global variables.\n"
        "[Done] Assigning global variables.\n\n"
        f"Making backup copy of config files at: '{VALID_CWD}' with timestamp: '{VALID_MOCK_TIMESTAMP}'\n"
        f"  Creating backup directory: '{VALID_CWD}/backup-{VALID_MOCK_TIMESTAMP}'\n"
        f"  Copied '{VALID_CWD}/host-configs' to '{VALID_CWD}/backup-{VALID_MOCK_TIMESTAMP}/host-configs'\n"
        f"  Copied '{VALID_CWD}/host-config-templates' to '{VALID_CWD}/backup-{VALID_MOCK_TIMESTAMP}/host-config-templates'\n"
        f"  Copied '{VALID_CWD}/extractors' to '{VALID_CWD}/backup-{VALID_MOCK_TIMESTAMP}/extractors'\n"
        f"  Copied '{VALID_CWD}/indices' to '{VALID_CWD}/backup-{VALID_MOCK_TIMESTAMP}/indices'\n"
        f"  Copied '{VALID_CWD}/inputs' to '{VALID_CWD}/backup-{VALID_MOCK_TIMESTAMP}/inputs'\n"
        f"  Copied '{VALID_CWD}/streams' to '{VALID_CWD}/backup-{VALID_MOCK_TIMESTAMP}/streams'\n"
        f"  Copied '{VALID_CWD}/schemas' to '{VALID_CWD}/backup-{VALID_MOCK_TIMESTAMP}/schemas'\n"
        "[Done] Making a backup copy of config files.\n\n"
    )
    assert captured.out == expected_output
    assert return_data == test_backup_dir
    assert os.path.exists(test_backup_dir)
    assert os.path.isdir(test_backup_dir)
    list_of_copied_dirs = os.listdir(test_backup_dir)
    assert len(list_of_copied_dirs) == 7
    if os.path.exists(test_backup_dir):
        shutil.rmtree(test_backup_dir) # cleanup test directory

def test_make_config_backup_verbose_pass_tmp_filesystem(tmp_path, monkeypatch, capsys) -> None:
    """tests.backup.test_make_config_backup_verbose_pass_tmp_filesystem function"""
    fake_args = ["arg1", "arg2", "arg3", True, tmp_path.as_posix()]
    monkeypatch.setattr("src.backup.generate_timestamp", lambda: VALID_MONKEYPATCH_DATETIMENOW)
    monkeypatch.setattr("os.makedirs", lambda *a, **k: None)
    monkeypatch.setattr("shutil.copytree", lambda src, dst: None)
    monkeypatch.setattr("os.listdir", lambda _: [])
    return_data = make_config_backup(fake_args,config_dirs=["/some/config1", "/some/config2"])
    captured = capsys.readouterr()
    expected_output = (
        f"Making backup copy of config files at: '{tmp_path}' with timestamp: '{VALID_MONKEYPATCH_DATETIMENOW}'\n"
        f"  Creating backup directory: '{tmp_path}/{VALID_BACKUP_FOLDERNAME}'\n"
        f"  Copied '/some/config1' to '{tmp_path}/{VALID_BACKUP_FOLDERNAME}/config1'\n"
        f"  Copied '/some/config2' to '{tmp_path}/{VALID_BACKUP_FOLDERNAME}/config2'\n"
        "[Done] Making a backup copy of config files.\n\n"
    )
    assert captured.out == expected_output
    fullpath = tmp_path.as_posix() + f"/{VALID_BACKUP_FOLDERNAME}"
    assert return_data == fullpath

def test_make_config_backup_nonverbose_pass_warn_backup_count(monkeypatch, tmp_path, capsys) -> None:
    """tests.backup.test_make_config_backup_nonverbose_pass_warn_backup_count function"""
    monkeypatch.setattr("os.listdir", lambda _: [f"graylogbackup-{i}" for i in range(5)])
    monkeypatch.setattr("os.makedirs", lambda *a, **k: None)
    monkeypatch.setattr("shutil.copytree", lambda src, dst: None)
    monkeypatch.setattr("src.backup.generate_timestamp", lambda: VALID_MONKEYPATCH_DATETIMENOW)
    return_data = make_config_backup(["a", "b", "c", False, tmp_path.as_posix()],config_dirs=["/test/dir1"])
    captured = capsys.readouterr()
    expected_output = (
        "[WARNING] 5 or more backups already exist. You may want to purge some old ones.\n" 
        f"Making backup copy of config files at: '{tmp_path}' with timestamp: '{VALID_MONKEYPATCH_DATETIMENOW}'\n"
        "[Done] Making a backup copy of config files.\n\n"
    )
    assert captured.out == expected_output
    fullpath = tmp_path.as_posix() + f"/{VALID_BACKUP_FOLDERNAME}"
    assert return_data == fullpath

def test_make_config_backup_pass_creates_sample_and_copies_all(tmp_path, monkeypatch) -> None:
    """tests.backup.test_make_config_backup_pass_creates_sample_and_copies_all function"""
    # Setup fake config dirs with files
    config1 = create_sample_config_dir(tmp_path, "configA")
    config2 = create_sample_config_dir(tmp_path, "configB")
    # Where the backup should go
    backup_base = tmp_path / "graylog" / "configs"
    backup_base.mkdir(parents=True)
    # Monkeypatch timestamp
    monkeypatch.setattr("src.backup.generate_timestamp", lambda: VALID_MONKEYPATCH_DATETIMENOW)
    function_args = ["arg1", "arg2", "arg3", backup_base.as_posix()]
    return_data = make_config_backup(args=function_args, config_dirs=[config1.as_posix(), config2.as_posix()])
    # Check if backup folder was created
    backup_fold_with_timestamp = "backup-" + VALID_MONKEYPATCH_DATETIMENOW
    expected_backup_folder = backup_base / backup_fold_with_timestamp
    assert return_data == expected_backup_folder.as_posix()
    assert expected_backup_folder.exists()
    assert expected_backup_folder.is_dir()
    # Check if directories and files are copied
    copied_configa = expected_backup_folder / "configA"
    copied_configb = expected_backup_folder / "configB"
    assert copied_configa.exists()
    assert copied_configb.exists()
    for i in range(2):
        assert (copied_configa / f"config_{i}.txt").read_text() == f"This is file {i}"
        assert (copied_configb / f"config_{i}.txt").read_text() == f"This is file {i}"

def test_make_config_backup_fail_patched_runtimeerror_exception(capsys) -> None:
    """tests.backup.test_make_config_backup_fail_patched_runtimeerror_exception function"""
    with patch("src.backup.list_existing_backups", side_effect=RuntimeError("Fake Exception Listing Backups")):
        with patch("src.backup.generate_timestamp", return_value=VALID_MOCK_TIMESTAMP): #patch timestamp
            with pytest.raises(SystemExit) as e:
                args = [VALID_SCRIPT, VALID_TOKEN, VALID_TEST_URL_NONEXIST, VALID_BOOL_VERBOSE_TRUE, VALID_CWD]
                set_global_vars(args) # have to call set global vars, othewise won't have valid global vars
                make_config_backup(args, global_vars.LIST_CONFIG_DIRECTORIES)
            captured = capsys.readouterr()
            expected_output = (
                "Assigning global variables.\n"
                "[Done] Assigning global variables.\n\n"
                "[ERROR] An runtime error occurred in make_config_backup: Fake Exception Listing Backups\n"
            )
            shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_make_config_backup_fail_patched_generic_exception(capsys) -> None:
    """tests.backup.test_make_config_backup_fail_patched_generic_exception function"""
    with patch("src.backup.generate_timestamp", side_effect=Exception("Fake Exception Generating Timestamp")): #patch timestamp
        with patch("src.backup.list_existing_backups", return_value=0):
            with pytest.raises(Exception):
                args = [VALID_SCRIPT, VALID_TOKEN, VALID_TEST_URL_NONEXIST, VALID_BOOL_VERBOSE_TRUE, VALID_CWD]
                set_global_vars(args) # have to call set global vars, othewise won't have valid global vars
                make_config_backup(args, global_vars.LIST_CONFIG_DIRECTORIES)
            captured = capsys.readouterr()
            expected_output = (
                "Assigning global variables.\n"
                "[Done] Assigning global variables.\n\n"
            )
            assert captured.out == expected_output

def test_generate_timestamp() -> None:
    """tests.backup.test_generate_timestamp function"""
    value=generate_timestamp()
    assert isinstance(value,str)
