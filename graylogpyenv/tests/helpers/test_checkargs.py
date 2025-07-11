"""Module:tests.helpers.test_checkargs"""
from unittest.mock import patch

from src.helpers import check_args
from tests.common.test_common import MOCK_TEST_URL
from tests.common.test_common import MOCK_TOKEN
from tests.common.test_common import MOCK_SCRIPT

INMOCK_TOKEN_SHORT = "SHORTTOKEN123"   # An invalid 13-char alphanumeric token
INMOCK_TOKEN_LONG = "LONGTOKENA1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R8S9T0U1V2W3X4Y5Z6" # An invalid 61-char alphanumeric token
INMOCK_TOKEN_NONALPHA = "A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6QR8S9T0U1V2W3X4Y5#$" # An invalid 52-char with non alphanumeric token
EXPECTED_VALID_OUTPUT = (
    "Checking arguments and validating the inputs.\n"
    "[Done] Checking arguments and validating the inputs.\n\n"
)

def test_check_args_pass_no_verbose_flag(capsys) -> None:
    """Function:test_check_args_pass_no_verbose_flag"""
    args = [MOCK_SCRIPT, MOCK_TOKEN, MOCK_TEST_URL]
    result = check_args(args)
    captured = capsys.readouterr()
    assert len(args) == 4
    assert result[0] == MOCK_SCRIPT
    assert result[1] == MOCK_TOKEN
    assert result[2] == MOCK_TEST_URL
    assert isinstance(result[3],str)
    assert captured.out == EXPECTED_VALID_OUTPUT

def test_check_args_pass_true_verbose_flag(capsys) -> None:
    """Function:test_check_args_pass_true_verbose_flag"""
    args = [MOCK_SCRIPT, MOCK_TOKEN, MOCK_TEST_URL, "TrUe"]
    result = check_args(args)
    captured = capsys.readouterr()
    assert len(args) == 5
    assert result[0] == MOCK_SCRIPT
    assert result[1] == MOCK_TOKEN
    assert result[2] == MOCK_TEST_URL
    assert result[3] is True
    assert isinstance(result[4],str)
    assert captured.out == EXPECTED_VALID_OUTPUT

def test_check_args_pass_false_verbose_flag(capsys) -> None:
    """Function:test_check_args_pass_false_verbose_flag"""
    args = [MOCK_SCRIPT, MOCK_TOKEN, MOCK_TEST_URL, "FaLsE"]
    result = check_args(args)
    captured = capsys.readouterr()
    assert len(args) == 5
    assert result[0] == MOCK_SCRIPT
    assert result[1] == MOCK_TOKEN
    assert result[2] == MOCK_TEST_URL
    assert result[3] is False
    assert isinstance(result[4],str)
    assert captured.out == EXPECTED_VALID_OUTPUT

def test_check_args_fail_too_few_arguments() -> None:
    """Function:test_check_args_fail_too_few_arguments"""
    args = [MOCK_SCRIPT, MOCK_TOKEN]
    result = check_args(args)
    assert "[ERROR] Wrong number of script arguments. Number of args passed:1" in result

def test_check_args_fail_too_many_arguments() -> None:
    """Function:test_check_args_fail_too_many_arguments"""
    args = [MOCK_SCRIPT, MOCK_TOKEN, MOCK_TEST_URL, "true", "extra"]
    result = check_args(args)
    assert "[ERROR] Wrong number of script arguments. Number of args passed:4" in result

def test_check_args_fail_token_short() -> None:
    """Function:test_check_args_fail_token_short"""
    args = [MOCK_SCRIPT, INMOCK_TOKEN_SHORT, MOCK_TEST_URL]
    result = check_args(args)
    assert "[ERROR] Token was wrong length" in result

def test_check_args_fail_token_long() -> None:
    """Function:test_check_args_fail_token_long"""
    args = [MOCK_SCRIPT, INMOCK_TOKEN_LONG, MOCK_TEST_URL]
    result = check_args(args)
    assert "[ERROR] Token was wrong length" in result

def test_check_args_fail_token_non_alphanumeric() -> None:
    """Function:test_check_args_fail_token_non_alphanumeric"""
    args = [MOCK_SCRIPT, INMOCK_TOKEN_NONALPHA, MOCK_TEST_URL]
    result = check_args(args)
    assert "[ERROR] Token had non alphanumeric characters" in result

def test_check_args_fail_bad_verbose_flag_short()-> None:
    """Function:test_check_args_fail_bad_verbose_flag_short"""
    args = [MOCK_SCRIPT, MOCK_TOKEN, MOCK_TEST_URL, "bad"]
    result = check_args(args)
    assert "[ERROR] Optional 3rd argument must be string: true or false." in result

def test_check_args_fail_bad_verbose_flag_long()-> None:
    """Function:test_check_args_fail_bad_verbose_flag_long"""
    args = [MOCK_SCRIPT, MOCK_TOKEN, MOCK_TEST_URL, "badflag"]
    result = check_args(args)
    assert "[ERROR] Optional 3rd argument must be string: true or false." in result

def test_check_args_fail_verbose_argument()-> None:
    """Function:test_check_args_fail_verbose_argument"""
    args = [MOCK_SCRIPT, MOCK_TOKEN, MOCK_TEST_URL, "maybe"]
    result = check_args(args)
    assert "[ERROR] Optional 3rd argument must be string: true or false" in result

def test_check_args_fail_invalid_verbose_type()-> None:
    """Function:test_check_args_fail_invalid_verbose_type"""
    args = [MOCK_SCRIPT, MOCK_TOKEN, MOCK_TEST_URL, 12345]  # Not a string
    result = check_args(args)
    assert "[ERROR] Optional 3rd argument must be string: true or false" in result

def test_os_error_handling()-> None:
    """Function:test_os_error_handling"""
    with patch('os.getcwd', side_effect=OSError("Mocked OS error")), patch('sys.exit') as mock_exit:
        args = [MOCK_SCRIPT, MOCK_TOKEN, MOCK_TEST_URL, "FaLsE"]
        check_args(args)
        mock_exit.assert_called_once_with(1)  # Check that sys.exit(1) was called
