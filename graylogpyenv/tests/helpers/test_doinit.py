"""tests.helpers test_doinit module"""
from unittest.mock import patch
from unittest import mock
import pytest

from src.helpers import do_init

VALID_SCRIPT = "graylog_setup.py"
VALID_TOKEN = "A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R8S9T0U1V2W3X4Y5Z6"
VALID_URL = "http://graylog.example.com"
VALID_ARGS = [VALID_SCRIPT, VALID_TOKEN, VALID_URL]
INVALID_ARGS = [VALID_SCRIPT, VALID_TOKEN]

@pytest.fixture(name="mocked_patches")
def mock_dependencies():
    """tests.helpers.mock_dependencies function"""
    with patch("src.helpers.print") as mock_print, \
         patch("src.helpers.sys.exit") as mock_exit, \
         patch("src.helpers.global_vars") as mock_globals, \
         patch("src.helpers.set_global_vars") as mock_set_globals, \
         patch("src.helpers.usage") as mock_usage, \
         patch("src.helpers.check_args") as mock_check_args, \
         patch("src.helpers.check_graylog_baseurl") as mock_check_baseurl, \
         patch("src.helpers.check_api_token") as mock_check_token:
        # Prepare global vars used in do_init
        mock_globals.STR_CLUSTER_URL = VALID_URL
        mock_globals.DICT_GET_HEADERS = {"Authorization": "Bearer mocktoken"}
        yield {
            "print": mock_print,
            "exit": mock_exit,
            "global_vars": mock_globals,
            "set_global_vars": mock_set_globals,
            "usage": mock_usage,
            "check_args": mock_check_args,
            "check_baseurl": mock_check_baseurl,
            "check_token": mock_check_token
        }

def test_do_init_pass_fixture(mocked_patches,capsys) -> None:
    """tests.helpers.test_do_init_pass_fixture function"""
    mocked_patches["check_args"].return_value = VALID_ARGS
    mocked_patches["check_baseurl"].return_value = True
    mocked_patches["check_token"].return_value = True
    result = do_init(VALID_ARGS)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert result == VALID_ARGS
    mocked_patches["set_global_vars"].assert_called_once_with(VALID_ARGS)
    mocked_patches["exit"].assert_not_called()

@mock.patch('src.helpers.check_args')
@mock.patch('src.helpers.usage')
def test_do_init_invalid_args(mock_usage, mock_check_args) -> None:
    """tests.helpers.test_do_init_invalid_args function"""
    mock_check_args.return_value = "Invalid arguments"
    with mock.patch('builtins.print') as mock_print:
        with pytest.raises(SystemExit) as e:
            do_init(INVALID_ARGS)
    mock_check_args.assert_called_once_with(INVALID_ARGS)
    mock_print.assert_called_once_with("Invalid arguments")
    mock_usage.assert_called_once_with(INVALID_ARGS)
    assert e.value.code == 1
    assert e.type == SystemExit

def test_do_init_fail_invalid_baseurl(mocked_patches) -> None:
    """ttests.helpers.test_do_init_fail_invalid_baseurl function"""
    mocked_patches["check_args"].return_value = ["arg1"]
    mocked_patches["check_baseurl"].return_value = "baseurl error"
    do_init(VALID_ARGS)
    mocked_patches["print"].assert_called_with("baseurl error")
    mocked_patches["exit"].assert_called_once_with(1)

def test_do_init_fail_invalid_token(mocked_patches) -> None:
    """tests.helpers.test_do_init_fail_invalid_token function"""
    mocked_patches["check_args"].return_value = ["arg1"]
    mocked_patches["check_baseurl"].return_value = True
    mocked_patches["check_token"].return_value = "token error"
    do_init(VALID_ARGS)
    mocked_patches["print"].assert_called_with("token error")
    mocked_patches["exit"].assert_called_once_with(1)
