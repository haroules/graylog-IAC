"""tests.helpers test_checkargs_verify module"""
from unittest.mock import patch

from src.helpers import check_args_verify

VALID_SCRIPT = "graylog_setup.py"
EXPECTED_VALID_OUTPUT = (
    "Checking arguments and validating the inputs.\n"
    "[Done] Checking arguments and validating the inputs.\n\n"
)

def test_check_args_verify_pass_no_verbose_flag(capsys) -> None:
    """tests.helpers.test_check_args_verify_pass_no_verbose_flag function"""
    args = [VALID_SCRIPT]
    result = check_args_verify(args)
    captured = capsys.readouterr()
    assert len(args) == 2
    assert result[0] == VALID_SCRIPT
    assert captured.out == EXPECTED_VALID_OUTPUT

def test_check_args_verify_pass_true_verbose_flag(capsys) -> None:
    """tests.helpers.test_check_args_verify_pass_true_verbose_flag function"""
    args = [VALID_SCRIPT, "TrUe"]
    result = check_args_verify(args)
    captured = capsys.readouterr()
    assert len(args) == 3
    assert result[0] == VALID_SCRIPT
    assert result[1] is True
    assert captured.out == EXPECTED_VALID_OUTPUT

def test_check_args_pass_false_verbose_flag(capsys) -> None:
    """tests.helpers.test_check_args_pass_false_verbose_flag function"""
    args = [VALID_SCRIPT,"FaLsE"]
    result = check_args_verify(args)
    captured = capsys.readouterr()
    assert len(args) == 3
    assert result[0] == VALID_SCRIPT
    assert result[1] is False
    assert captured.out == EXPECTED_VALID_OUTPUT

def test_check_args_fail_too_many_arguments() -> None:
    """tests.helpers.test_check_args_fail_too_many_arguments function"""
    args = [VALID_SCRIPT,"true", "extra"]
    result = check_args_verify(args)
    assert "[ERROR] Wrong number of script arguments. Number of args passed:2" in result

def test_check_args_fail_bad_verbose_flag_short() -> None:
    """tests.helpers.test_check_args_fail_bad_verbose_flag_short function"""
    args = [VALID_SCRIPT, "bad"]
    result = check_args_verify(args)
    assert "[ERROR] Optional argument must be string: true or false." in result

def test_check_args_fail_bad_verbose_flag_long() -> None:
    """tests.helpers.test_check_args_fail_bad_verbose_flag_long function"""
    args = [VALID_SCRIPT, "badflag"]
    result = check_args_verify(args)
    assert "[ERROR] Optional argument must be string: true or false." in result

def test_check_args_fail_verbose_argument() -> None:
    """tests.helpers.test_check_args_fail_verbose_argument function"""
    args = [VALID_SCRIPT, "maybe"]
    result = check_args_verify(args)
    assert "[ERROR] Optional argument must be string: true or false" in result

def test_check_args_fail_invalid_verbose_type() -> None:
    """tests.helpers.test_check_args_fail_invalid_verbose_type function"""
    args = [VALID_SCRIPT, 12345]  # Not a string
    result = check_args_verify(args)
    assert "[ERROR] Optional argument must be string: true or false" in result

def test_os_error_handling_fail() -> None:
    """tests.helpers.test_os_error_handling_fail function"""
    with patch('os.getcwd', side_effect=OSError("Mocked OS error")), patch('sys.exit') as mock_exit:
        args = [VALID_SCRIPT, "FaLsE"]
        check_args_verify(args)
        mock_exit.assert_called_once_with(1)  # Check that sys.exit(1) was called
