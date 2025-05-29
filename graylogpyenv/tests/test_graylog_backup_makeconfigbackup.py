import pytest
import os
import shutil
import graylog_global_vars
from datetime import datetime
from typing import Tuple
from pathlib import Path
from unittest import mock
from unittest.mock import patch, MagicMock
from src.graylog_helpers import set_global_vars
from src.graylog_backup import make_config_backup
from src.graylog_backup import list_existing_backups
from src.graylog_backup import create_backup_folder
from src.graylog_backup import copy_directories
from src.graylog_backup import generate_timestamp

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

@pytest.fixture
def mock_filesystem(monkeypatch):
    monkeypatch.setattr("os.makedirs", lambda *a, **k: None)
    monkeypatch.setattr("shutil.copytree", lambda src, dst: None)
    monkeypatch.setattr("os.listdir", lambda _: [])

def create_sample_config_dir(base_dir: Path, name: str, file_count: int = 2) -> Path:
    config_dir = base_dir / name
    config_dir.mkdir()
    for i in range(file_count):
        file_path = config_dir / f"config_{i}.txt"
        file_path.write_text(f"This is file {i}")
    return config_dir

def test_make_config_backup_nonverbose_pass(capsys,mocker):
    test_backup_dir = VALID_CWD + "/backup-" + VALID_MOCK_TIMESTAMP
    if (os.path.exists(test_backup_dir)): shutil.rmtree(test_backup_dir) # remove directory created by test before and after test
    mocker.patch("src.graylog_backup.generate_timestamp", return_value=VALID_MOCK_TIMESTAMP) #patch timestamp
    mocker.patch("src.graylog_backup.list_existing_backups", return_value=0) #patch list backups to 0 so dont get warning about 5 or more backups
    args = [VALID_SCRIPT, VALID_TOKEN, VALID_TEST_URL_NONEXIST, VALID_BOOL_VERBOSE_FALSE, VALID_CWD]
    set_global_vars(args) # have to call set global vars, othewise won't have valid global vars
    tuple_return_data: Tuple[bool,str] = make_config_backup(args, graylog_global_vars.list_config_directories)
    func_success, pathormessage = tuple_return_data
    captured = capsys.readouterr()
    expected_output = (
        "Assigning global variables.\n"
        "[Done] Assigning global variables.\n\n"
        f"Making safe copy of config files before modification in dir: '{VALID_CWD}' with timestamp: '{VALID_MOCK_TIMESTAMP}'\n"
        "[Done] Making a safe copy of config files.\n\n"
    )
    assert captured.out == expected_output
    assert func_success == True
    assert pathormessage == test_backup_dir
    assert os.path.exists(test_backup_dir)
    assert os.path.isdir(test_backup_dir)
    list_of_copied_dirs = os.listdir(test_backup_dir)
    assert len(list_of_copied_dirs) == 7
    if (os.path.exists(test_backup_dir)): shutil.rmtree(test_backup_dir) # cleanup test directory

def test_make_config_backup_verbose_pass_valid(capsys,mocker):
    test_backup_dir = VALID_CWD + "/backup-" + VALID_MOCK_TIMESTAMP
    if (os.path.exists(test_backup_dir)): shutil.rmtree(test_backup_dir) # remove directory created by test before and after test
    mocker.patch("src.graylog_backup.generate_timestamp", return_value=VALID_MOCK_TIMESTAMP) #patch timestamp
    mocker.patch("src.graylog_backup.list_existing_backups", return_value=0) #patch list backups to 0 so dont get warning about 5 or more backups
    args = [VALID_SCRIPT, VALID_TOKEN, VALID_TEST_URL_NONEXIST, VALID_BOOL_VERBOSE_TRUE, VALID_CWD]
    set_global_vars(args) # have to call set global vars, othewise won't have valid global vars
    tuple_return_data: Tuple[bool,str] = make_config_backup(args, graylog_global_vars.list_config_directories)
    func_success, pathormessage = tuple_return_data
    captured = capsys.readouterr()
    expected_output = (
        "Assigning global variables.\n"
        "[Done] Assigning global variables.\n\n"
        f"Making safe copy of config files before modification in dir: '{VALID_CWD}' with timestamp: '{VALID_MOCK_TIMESTAMP}'\n"
        f"  Creating backup directory: '{VALID_CWD}/backup-{VALID_MOCK_TIMESTAMP}'\n"
        f"  Copied '{VALID_CWD}/host-configs' to '{VALID_CWD}/backup-{VALID_MOCK_TIMESTAMP}/host-configs'\n"
        f"  Copied '{VALID_CWD}/host-config-templates' to '{VALID_CWD}/backup-{VALID_MOCK_TIMESTAMP}/host-config-templates'\n"
        f"  Copied '{VALID_CWD}/extractors' to '{VALID_CWD}/backup-{VALID_MOCK_TIMESTAMP}/extractors'\n"
        f"  Copied '{VALID_CWD}/indices' to '{VALID_CWD}/backup-{VALID_MOCK_TIMESTAMP}/indices'\n"
        f"  Copied '{VALID_CWD}/inputs' to '{VALID_CWD}/backup-{VALID_MOCK_TIMESTAMP}/inputs'\n"
        f"  Copied '{VALID_CWD}/streams' to '{VALID_CWD}/backup-{VALID_MOCK_TIMESTAMP}/streams'\n"
        f"  Copied '{VALID_CWD}/schemas' to '{VALID_CWD}/backup-{VALID_MOCK_TIMESTAMP}/schemas'\n"
        "[Done] Making a safe copy of config files.\n\n"
    )
    assert captured.out == expected_output
    assert func_success == True
    assert pathormessage == test_backup_dir
    assert os.path.exists(test_backup_dir)
    assert os.path.isdir(test_backup_dir)
    list_of_copied_dirs = os.listdir(test_backup_dir)
    assert len(list_of_copied_dirs) == 7
    if (os.path.exists(test_backup_dir)): shutil.rmtree(test_backup_dir) # cleanup test directory

def test_make_config_backup_verbose_pass_testfilesystem(tmp_path, monkeypatch, mock_filesystem, capsys):
    fake_args = ["arg1", "arg2", "arg3", True, tmp_path.as_posix()]
    monkeypatch.setattr("src.graylog_backup.generate_timestamp", lambda: VALID_MONKEYPATCH_DATETIMENOW)
    tuple_return_data: Tuple[bool,str] = make_config_backup(fake_args,config_dirs=["/some/config1", "/some/config2"])
    successful, pathormessage = tuple_return_data
    captured = capsys.readouterr()
    expected_output = (
        f"Making safe copy of config files before modification in dir: '{tmp_path}' with timestamp: '{VALID_MONKEYPATCH_DATETIMENOW}'\n"
        f"  Creating backup directory: '{tmp_path}/{VALID_BACKUP_FOLDERNAME}'\n"
        f"  Copied '/some/config1' to '{tmp_path}/{VALID_BACKUP_FOLDERNAME}/config1'\n"
        f"  Copied '/some/config2' to '{tmp_path}/{VALID_BACKUP_FOLDERNAME}/config2'\n"
        "[Done] Making a safe copy of config files.\n\n"
    )
    assert captured.out == expected_output
    assert successful is True
    fullpath = tmp_path.as_posix() + f"/{VALID_BACKUP_FOLDERNAME}"
    assert pathormessage == fullpath

def test_make_config_backup_nonverbose_pass_testfilesystem(tmp_path, monkeypatch, mock_filesystem, capsys):
    fake_args = ["arg1", "arg2", "arg3", False, tmp_path.as_posix()]
    monkeypatch.setattr("src.graylog_backup.generate_timestamp", lambda: VALID_MONKEYPATCH_DATETIMENOW)
    tuple_return_data: Tuple[bool,str] = make_config_backup(fake_args,config_dirs=["/some/config1", "/some/config2"])
    successful, pathormessage = tuple_return_data
    captured = capsys.readouterr()
    expected_output = (
        f"Making safe copy of config files before modification in dir: '{tmp_path}' with timestamp: '{VALID_MONKEYPATCH_DATETIMENOW}'\n"
        "[Done] Making a safe copy of config files.\n\n"
    )
    assert captured.out == expected_output
    assert successful is True
    fullpath = tmp_path.as_posix() + f"/{VALID_BACKUP_FOLDERNAME}"
    assert pathormessage == fullpath

def test_make_config_backup_nonverbose_pass_warn_backup_count(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr("os.listdir", lambda _: [f"graylogbackup-{i}" for i in range(5)])
    monkeypatch.setattr("os.makedirs", lambda *a, **k: None)
    monkeypatch.setattr("shutil.copytree", lambda src, dst: None)
    monkeypatch.setattr("src.graylog_backup.generate_timestamp", lambda: VALID_MONKEYPATCH_DATETIMENOW)
    tuple_return_data: Tuple[bool,str] = make_config_backup(["a", "b", "c", False, tmp_path.as_posix()],config_dirs=["/test/dir1"])
    successful, pathormessage = tuple_return_data
    captured = capsys.readouterr()
    expected_output = (
        "[WARNING] 5 or more backups already exist. You may want to purge some old ones.\n" 
        f"Making safe copy of config files before modification in dir: '{tmp_path}' with timestamp: '{VALID_MONKEYPATCH_DATETIMENOW}'\n"
        "[Done] Making a safe copy of config files.\n\n"
    )
    assert captured.out == expected_output
    assert successful is True
    fullpath = tmp_path.as_posix() + f"/{VALID_BACKUP_FOLDERNAME}"
    assert pathormessage == fullpath

def test_make_config_backup_pass_creates_sample_and_copies_all(tmp_path, monkeypatch):
    # Setup fake config dirs with files
    config1 = create_sample_config_dir(tmp_path, "configA")
    config2 = create_sample_config_dir(tmp_path, "configB")
    # Where the backup should go
    backup_base = tmp_path / "graylog" / "configs"
    backup_base.mkdir(parents=True)
    # Monkeypatch timestamp
    monkeypatch.setattr("src.graylog_backup.generate_timestamp", lambda: VALID_MONKEYPATCH_DATETIMENOW)
    tuple_return_data: Tuple[bool,str] = make_config_backup(args=["arg1", "arg2", "arg3", backup_base.as_posix()], config_dirs=[config1.as_posix(), config2.as_posix()])
    func_success, pathormessage = tuple_return_data
    assert func_success is True
    # Check if backup folder was created
    backup_fold_with_timestamp = "backup-" + VALID_MONKEYPATCH_DATETIMENOW
    expected_backup_folder = backup_base / backup_fold_with_timestamp
    assert pathormessage == expected_backup_folder.as_posix() 
    assert expected_backup_folder.exists()
    assert expected_backup_folder.is_dir()
    # Check if directories and files are copied
    copied_configA = expected_backup_folder / "configA"
    copied_configB = expected_backup_folder / "configB"
    assert copied_configA.exists()
    assert copied_configB.exists()
    for i in range(2):
        assert (copied_configA / f"config_{i}.txt").read_text() == f"This is file {i}"
        assert (copied_configB / f"config_{i}.txt").read_text() == f"This is file {i}"

def test_make_config_backup_fail_patched_createbackupfolder():
    with patch("src.graylog_backup.list_existing_backups", return_value=0):
        with patch("src.graylog_backup.generate_timestamp", return_value=VALID_MOCK_TIMESTAMP): #patch timestamp
            with patch("src.graylog_backup.create_backup_folder", return_value = [False, "Some Error"]):
                args = [VALID_SCRIPT, VALID_TOKEN, VALID_TEST_URL_NONEXIST, VALID_BOOL_VERBOSE_TRUE, VALID_CWD]
                set_global_vars(args) # have to call set global vars, othewise won't have valid global vars
                tuple_return_data: Tuple[bool,str] = make_config_backup(args, graylog_global_vars.list_config_directories)
                func_success, pathormessage = tuple_return_data
            assert func_success == False
            assert pathormessage == "Some Error"

def test_make_config_backup_fail_patched_runtimeerror_exception(capsys):
    with patch("src.graylog_backup.list_existing_backups", side_effect=RuntimeError("Fake Exception Listing Backups")):
        with patch("src.graylog_backup.generate_timestamp", return_value=VALID_MOCK_TIMESTAMP): #patch timestamp
            args = [VALID_SCRIPT, VALID_TOKEN, VALID_TEST_URL_NONEXIST, VALID_BOOL_VERBOSE_TRUE, VALID_CWD]
            set_global_vars(args) # have to call set global vars, othewise won't have valid global vars
            tuple_return_data: Tuple[bool,str] = make_config_backup(args, graylog_global_vars.list_config_directories)
            func_success, pathormessage = tuple_return_data
            captured = capsys.readouterr()
            expected_output = (
                "Assigning global variables.\n"
                "[Done] Assigning global variables.\n\n"
            )
            assert captured.out == expected_output
            assert func_success == False
            assert pathormessage == "[ERROR] An runtime error occurred: Fake Exception Listing Backups"

def test_make_config_backup_fail_patched_generic_exception(capsys):
    with patch("src.graylog_backup.generate_timestamp", side_effect=Exception("Fake Exception Generating Timestamp")): #patch timestamp
        with patch("src.graylog_backup.list_existing_backups", return_value=0):
            args = [VALID_SCRIPT, VALID_TOKEN, VALID_TEST_URL_NONEXIST, VALID_BOOL_VERBOSE_TRUE, VALID_CWD]
            set_global_vars(args) # have to call set global vars, othewise won't have valid global vars
            tuple_return_data: Tuple[bool,str] = make_config_backup(args, graylog_global_vars.list_config_directories)
            func_success, pathormessage = tuple_return_data
            captured = capsys.readouterr()
            expected_output = (
                "Assigning global variables.\n"
                "[Done] Assigning global variables.\n\n"
            )
            assert captured.out == expected_output
            assert func_success == False
            assert pathormessage == "[ERROR] An generic exception occurred: Fake Exception Generating Timestamp"

def test_make_config_backup_fail_folder_creation_fileexists_error(monkeypatch, tmp_path):
    def raise_oserror(*args, **kwargs):
        raise FileExistsError("folder already exists")
    monkeypatch.setattr("os.makedirs", raise_oserror)
    monkeypatch.setattr("os.listdir", lambda _: [])
    monkeypatch.setattr("shutil.copytree", lambda src, dst: None)
    monkeypatch.setattr("src.graylog_backup.generate_timestamp", lambda: VALID_MONKEYPATCH_DATETIMENOW)
    tuple_return_data: Tuple[bool,str] = make_config_backup(["a", "b", "c", tmp_path.as_posix()],config_dirs=["/dir"])
    successful, pathormessage = tuple_return_data
    assert successful is False
    assert pathormessage == f"[ERROR] An generic exception occurred: folder already exists"

def test_make_config_backup_fail_folder_creation_filenotfound_error(monkeypatch, tmp_path):
    def raise_oserror(*args, **kwargs):
        raise FileNotFoundError("directory doesn't exist")
    monkeypatch.setattr("os.makedirs", raise_oserror)
    monkeypatch.setattr("os.listdir", lambda _: [])
    monkeypatch.setattr("shutil.copytree", lambda src, dst: None)
    monkeypatch.setattr("src.graylog_backup.generate_timestamp", lambda: VALID_MONKEYPATCH_DATETIMENOW)
    tuple_return_data: Tuple[bool,str] = make_config_backup(["a", "b", "c", tmp_path.as_posix()],config_dirs=["/dir"])
    successful, pathormessage = tuple_return_data
    assert successful is False
    assert pathormessage == f"[ERROR] An generic exception occurred: directory doesn't exist"

def test_list_existing_backups_pass_mocked_filesystem(tmp_path):
    config1 = create_sample_config_dir(tmp_path, "backup-A")
    config2 = create_sample_config_dir(tmp_path, "backup-B")
    config2 = create_sample_config_dir(tmp_path, "backup-C")
    result = list_existing_backups(tmp_path)
    assert result == 3

def test_list_existing_backups_fail_raised_filenotfound(capsys):
    with pytest.raises(FileNotFoundError) as e:
        list_existing_backups("bad-path")
    captured = capsys.readouterr()
    assert captured.out == "[ERROR] Failed listing backup folders: 'bad-path'. Error was: [Errno 2] No such file or directory: 'bad-path'\n"

def test_list_existing_backups_fail_raised_oserror(capsys):
    with pytest.raises(os.error) as e:
        list_existing_backups(True)
    captured = capsys.readouterr()
    assert captured.out == "[ERROR] Failed listing backup folders: 'True'. Error was: [Errno 20] Not a directory: True\n"

def test_create_backup_folder_fail_patched_oserror(capsys):
    with patch('os.makedirs', side_effect=OSError("Mocked OSError")):
        with pytest.raises(OSError) as e:
            create_backup_folder("bad_path",VALID_MOCK_TIMESTAMP, False)
        captured = capsys.readouterr()
        assert str(e.value) == "Mocked OSError"
        assert captured.out == "[ERROR] An OSError occurred: Mocked OSError\n"

def test_create_backup_folder_fail_patched_fileexists_error(capsys):
    with patch('os.makedirs', side_effect=FileExistsError("Mocked File Exists Error")):
        with pytest.raises(FileExistsError) as e:
            badpath_arg = "bad_path"
            create_backup_folder(badpath_arg,VALID_MOCK_TIMESTAMP, False)
        captured = capsys.readouterr()
        assert str(e.value) == "Mocked File Exists Error"
        assert captured.out == f"[ERROR] Directory '{badpath_arg}/backup-{VALID_MOCK_TIMESTAMP}' already exists.\n"

def test_create_backup_folder_fail_patched_filenotfound_error(capsys):
    with patch('os.makedirs', side_effect=FileNotFoundError("Mocked FileNotFound Error")):
        with pytest.raises(FileNotFoundError) as e:
            badpath_arg = "bad_path"
            create_backup_folder(badpath_arg,VALID_MOCK_TIMESTAMP, False)
        captured = capsys.readouterr()
        assert str(e.value) == "Mocked FileNotFound Error"
        assert captured.out == f"[ERROR] A parent directory in '{badpath_arg}/backup-{VALID_MOCK_TIMESTAMP}' does not exist.\n"

def test_create_backup_folder_pass_nonverbose(capsys, monkeypatch):
    test_backup_dir = VALID_CWD + "/backup-" + VALID_MOCK_TIMESTAMP
    monkeypatch.setattr("src.graylog_backup.generate_timestamp", lambda: VALID_MONKEYPATCH_DATETIMENOW)
    create_backup_folder(VALID_CWD,VALID_MOCK_TIMESTAMP, False)
    captured = capsys.readouterr()
    assert captured.out == ""
    if (os.path.exists(test_backup_dir)): shutil.rmtree(test_backup_dir) # remove directory created by test before and after test

def test_create_backup_folder_pass_verbose(capsys, monkeypatch):
    test_backup_dir = VALID_CWD + "/backup-" + VALID_MOCK_TIMESTAMP
    monkeypatch.setattr("src.graylog_backup.generate_timestamp", lambda: VALID_MONKEYPATCH_DATETIMENOW)
    create_backup_folder(VALID_CWD,VALID_MOCK_TIMESTAMP, True)
    captured = capsys.readouterr()
    assert captured.out == f"  Creating backup directory: '{test_backup_dir}'\n"
    if (os.path.exists(test_backup_dir)): shutil.rmtree(test_backup_dir) # remove directory created by test before and after test

def test_copy_directories_pass_nonverbose(tmp_path):
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
    copied_configA = backup_base / "configA"
    copied_configB = backup_base / "configB"
    assert copied_configA.exists()
    assert copied_configB.exists()
    for i in range(2):
        assert (copied_configA / f"config_{i}.txt").read_text() == f"This is file {i}"
        assert (copied_configB / f"config_{i}.txt").read_text() == f"This is file {i}"

def test_copy_directories_pass_verbose(tmp_path, capsys):
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
    copied_configA = backup_base / "configA"
    copied_configB = backup_base / "configB"
    assert copied_configA.exists()
    assert copied_configB.exists()
    for i in range(2):
        assert (copied_configA / f"config_{i}.txt").read_text() == f"This is file {i}"
        assert (copied_configB / f"config_{i}.txt").read_text() == f"This is file {i}"

def test_copy_directories_fail_raised_oserror(monkeypatch, capsys):
    directories = ['/mock/source']
    dest_base = '/mock/destination'

    monkeypatch.setattr(os.path, 'basename', lambda path: 'source')
    monkeypatch.setattr(shutil, 'copytree', mock.Mock(side_effect=OSError("Mocked OS error")))

    with pytest.raises(SystemExit) as e:
        copy_directories(directories, dest_base, bool_verbose=False)
    captured = capsys.readouterr()
    assert captured.out == "[ERROR]: OS related error: Mocked OS error\n"
    assert e.type == SystemExit
    assert e.value.code == 1

def test_copy_directories_fail_raised_shutilsamefileerror(monkeypatch,capsys):
    directories = ['/mock/source']
    dest_base = '/mock/destination'

    monkeypatch.setattr(os.path, 'basename', lambda path: 'source')
    monkeypatch.setattr(shutil, 'copytree', mock.Mock(side_effect=shutil.SameFileError("same file")))

    with pytest.raises(SystemExit) as e:
        copy_directories(directories, dest_base, bool_verbose=False)
    captured = capsys.readouterr()
    assert captured.out == "[ERROR]: OS related error: same file\n"
    assert e.type == SystemExit
    assert e.value.code == 1

def test_copy_directories_fail_raised_shutilerror(monkeypatch,capsys):
    directories = ['/mock/source']
    dest_base = '/mock/destination'

    monkeypatch.setattr(os.path, 'basename', lambda path: 'source')
    monkeypatch.setattr(shutil, 'copytree', mock.Mock(side_effect=shutil.Error("generic shutil error")))

    with pytest.raises(SystemExit) as e:
        copy_directories(directories, dest_base, bool_verbose=False)
    captured = capsys.readouterr()
    assert captured.out == "[ERROR]: OS related error: generic shutil error\n"
    assert e.type == SystemExit
    assert e.value.code == 1

def test_generate_timestamp():
    value=generate_timestamp()
    assert type(value) == str