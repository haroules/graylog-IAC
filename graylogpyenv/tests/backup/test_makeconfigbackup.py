"""Module:tests.backup.test_backup_makeconfigbackup"""
import os
from datetime import datetime
from unittest.mock import patch
import pytest

import global_vars
from src.helpers import set_global_vars
from src.backup import make_config_backup
from src.backup import generate_timestamp
from tests.common.test_common import shared_asserts
from tests.common.test_common import BOOL_VERBOSE_TRUE
from tests.common.test_common import BOOL_VERBOSE_FALSE
from tests.common.test_common import MOCK_TEST_URL
from tests.common.test_common import MOCK_SCRIPT
from tests.common.test_common import MOCK_TOKEN

VALID_CWD = os.path.dirname(os.getcwd())
MOCK_TIMESTAMP = "04-19-2025-010000"
MOCK_DATETIMENOW = "20250419-010000"
BACKUP_FOLDERNAME = f"backup-{MOCK_DATETIMENOW}"
FAKE_NOW = datetime(2022, 10, 21, 22, 22, 22).strftime("%m-%d-%Y-%H%M%S")

def test_make_config_backup_pass(tmp_path, monkeypatch, capsys) -> None:
    """Function:test_make_config_backup_pass"""
    fake_args = ["arg1", "arg2", "arg3", BOOL_VERBOSE_TRUE, tmp_path.as_posix()]
    monkeypatch.setattr("src.backup.generate_timestamp", lambda: MOCK_DATETIMENOW)
    monkeypatch.setattr("os.makedirs", lambda *a, **k: None)
    monkeypatch.setattr("shutil.copytree", lambda src, dst: None)
    monkeypatch.setattr("os.listdir", lambda _: [])
    return_data = make_config_backup(fake_args,config_dirs=["/some/config1", "/some/config2"])
    captured = capsys.readouterr()
    expected_output = (
        f"Making backup copy of config files at: '{tmp_path}' with timestamp: '{MOCK_DATETIMENOW}'\n"
        f"  Creating backup directory: '{tmp_path}/{BACKUP_FOLDERNAME}'\n"
        f"  Copied '/some/config1' to '{tmp_path}/{BACKUP_FOLDERNAME}/config1'\n"
        f"  Copied '/some/config2' to '{tmp_path}/{BACKUP_FOLDERNAME}/config2'\n"
        "[Done] Making a backup copy of config files.\n\n"
    )
    assert captured.out == expected_output
    fullpath = tmp_path.as_posix() + f"/{BACKUP_FOLDERNAME}"
    assert return_data == fullpath

def test_make_config_backup_pass_warn_backup_count(monkeypatch, tmp_path, capsys) -> None:
    """Function:test_make_config_backup_pass_warn_backup_count"""
    monkeypatch.setattr("os.listdir", lambda _: [f"graylogbackup-{i}" for i in range(5)])
    monkeypatch.setattr("os.makedirs", lambda *a, **k: None)
    monkeypatch.setattr("shutil.copytree", lambda src, dst: None)
    monkeypatch.setattr("src.backup.generate_timestamp", lambda: MOCK_DATETIMENOW)
    return_data = make_config_backup(["a", "b", "c", BOOL_VERBOSE_FALSE, tmp_path.as_posix()],config_dirs=["/test/dir1"])
    captured = capsys.readouterr()
    expected_output = (
        "[WARNING] 5 or more backups already exist. You may want to purge some old ones.\n" 
        f"Making backup copy of config files at: '{tmp_path}' with timestamp: '{MOCK_DATETIMENOW}'\n"
        "[Done] Making a backup copy of config files.\n\n"
    )
    assert captured.out == expected_output
    fullpath = tmp_path.as_posix() + f"/{BACKUP_FOLDERNAME}"
    assert return_data == fullpath

def test_make_config_backup_fail_runtimeerror_exception(capsys) -> None:
    """Function:test_make_config_backup_fail_runtimeerror_exception"""
    with patch("src.backup.list_existing_backups", side_effect=RuntimeError("Fake Exception Listing Backups")):
        with patch("src.backup.generate_timestamp", return_value=MOCK_TIMESTAMP): #patch timestamp
            with pytest.raises(SystemExit) as e:
                args = [MOCK_SCRIPT, MOCK_TOKEN, MOCK_TEST_URL, BOOL_VERBOSE_TRUE, VALID_CWD]
                set_global_vars(args) # have to call set global vars, othewise won't have valid global vars
                make_config_backup(args, global_vars.LIST_CONFIG_DIRECTORIES)
            captured = capsys.readouterr()
            expected_output = (
                "Assigning global variables.\n"
                "[Done] Assigning global variables.\n\n"
                "[ERROR] An runtime error occurred in make_config_backup: Fake Exception Listing Backups\n"
            )
            shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_generate_timestamp() -> None:
    """Function:test_generate_timestamp"""
    value=generate_timestamp()
    assert isinstance(value,str)
