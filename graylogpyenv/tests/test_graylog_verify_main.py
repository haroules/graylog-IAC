"""Module:test_graylog_verify_main"""

from unittest.mock import patch
from unittest import mock
import pytest
import graylog_verify

args = ["graylog_verify.py"]

def test_graylog_verify_main_init() -> None:
    """Function:test_graylog_verify_main_init"""
    with patch.object(graylog_verify,"main", return_value=33):
        with patch.object(graylog_verify, "__name__", "__main__"):
            with patch.object(graylog_verify, "check_args_verify", return_value=args):
                with patch.object(graylog_verify.sys,'exit') as mock_exit:
                    graylog_verify.init()
                    assert mock_exit.call_args[0][0] == 33

@mock.patch('graylog_verify.verify_stream_rules')
@mock.patch('graylog_verify.verify_hostname_in_config')
@mock.patch('graylog_verify.verify_hostconfig_integrity')
@mock.patch('graylog_verify.verify_hostconfigfiles_deps_schema')
@mock.patch('graylog_verify.verify_hostconfigfiles_schema')
@mock.patch('graylog_verify.verify_configfiles_filesystem')
@mock.patch('graylog_verify.set_global_vars_verify')
@mock.patch('graylog_verify.check_args_verify')
def test_graylog_verify_main_pass(
    mock_check_args_verify, mock_set_global_vars_verify,
    mock_verify_configfiles_filesystem, mock_verify_hostconfigfiles_schema,
    mock_verify_hostconfigfiles_deps_schema, mock_verify_hostconfig_integrity,
    mock_verify_hostname_in_config, mock_verify_stream_rules
) -> None:
    """Function:test_graylog_verify_main_pass"""
    mock_verify_configfiles_filesystem.return_value = None
    mock_verify_hostconfigfiles_schema.return_value = None
    mock_verify_hostconfigfiles_deps_schema.return_value = None
    mock_verify_hostconfig_integrity.return_value = None
    mock_verify_hostname_in_config.return_value = None
    mock_verify_stream_rules.return_value = None
    mock_set_global_vars_verify.return_value = None
    mock_check_args_verify.return_value = args
    graylog_verify.main()
    mock_check_args_verify.assert_called_once()
    mock_set_global_vars_verify.assert_called_once()

@mock.patch('graylog_verify.check_args_verify')
def test_graylog_verify_main_fail_invalid_args(mock_check_args_verify) -> None:
    """Function:test_graylog_verify_main_fail_invalid_args"""
    mock_check_args_verify.return_value = "Invalid arguments"
    with mock.patch('builtins.print') as mock_print, mock.patch('sys.argv',
            ["graylog_verify.py"]), pytest.raises(SystemExit) as e:
        graylog_verify.main()
    mock_print.assert_called_with("  -Setting verbose to False will supress output.\n")
    assert e.value.code == 1
