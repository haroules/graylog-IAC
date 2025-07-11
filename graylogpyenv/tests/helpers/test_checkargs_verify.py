"""Module:tests.helpers.test_checkargs_verify"""
from unittest.mock import patch

from src.helpers import check_args_verify
from tests.common.test_common import MOCK_SCRIPT

EXPECTED_VALID_OUTPUT = (
    "Checking arguments and validating the inputs.\n"
    "[Done] Checking arguments and validating the inputs.\n\n"
)

def test_check_args_verify_pass_no_verbose_flag(capsys) -> None:
    """Function:test_check_args_verify_pass_no_verbose_flag"""
    args = [MOCK_SCRIPT]
    result = check_args_verify(args)
    captured = capsys.readouterr()
    assert len(args) == 2
    assert result[0] == MOCK_SCRIPT
    assert captured.out == EXPECTED_VALID_OUTPUT

def test_check_args_verify_pass_true_verbose_flag(capsys) -> None:
    """Function:test_check_args_verify_pass_true_verbose_flag"""
    args = [MOCK_SCRIPT, "TrUe"]
    result = check_args_verify(args)
    captured = capsys.readouterr()
    assert len(args) == 3
    assert result[0] == MOCK_SCRIPT
    assert result[1] is True
    assert captured.out == EXPECTED_VALID_OUTPUT

def test_check_args_pass_false_verbose_flag(capsys) -> None:
    """Function:test_check_args_pass_false_verbose_flag"""
    args = [MOCK_SCRIPT,"FaLsE"]
    result = check_args_verify(args)
    captured = capsys.readouterr()
    assert len(args) == 3
    assert result[0] == MOCK_SCRIPT
    assert result[1] is False
    assert captured.out == EXPECTED_VALID_OUTPUT

def test_check_args_fail_too_many_arguments() -> None:
    """Function:test_check_args_fail_too_many_arguments"""
    args = [MOCK_SCRIPT,"true", "extra"]
    result = check_args_verify(args)
    assert "[ERROR] Wrong number of script arguments. Number of args passed:2" in result

def test_check_args_fail_bad_verbose_flag_short() -> None:
    """Function:test_check_args_fail_bad_verbose_flag_short"""
    args = [MOCK_SCRIPT, "bad"]
    result = check_args_verify(args)
    assert "[ERROR] Optional argument must be string: true or false." in result

def test_check_args_fail_bad_verbose_flag_long() -> None:
    """Function:test_check_args_fail_bad_verbose_flag_long"""
    args = [MOCK_SCRIPT, "badflag"]
    result = check_args_verify(args)
    assert "[ERROR] Optional argument must be string: true or false." in result

def test_check_args_fail_verbose_argument() -> None:
    """Function:test_check_args_fail_verbose_argument"""
    args = [MOCK_SCRIPT, "maybe"]
    result = check_args_verify(args)
    assert "[ERROR] Optional argument must be string: true or false" in result

def test_check_args_fail_invalid_verbose_type() -> None:
    """Function:test_check_args_fail_invalid_verbose_type"""
    args = [MOCK_SCRIPT, 12345]  # Not a string
    result = check_args_verify(args)
    assert "[ERROR] Optional argument must be string: true or false" in result

def test_os_error_handling_fail() -> None:
    """Function:test_os_error_handling_fail"""
    with patch('os.getcwd', side_effect=OSError("Mocked OS error")), patch('sys.exit') as mock_exit:
        args = [MOCK_SCRIPT, "FaLsE"]
        check_args_verify(args)
        mock_exit.assert_called_once_with(1)
