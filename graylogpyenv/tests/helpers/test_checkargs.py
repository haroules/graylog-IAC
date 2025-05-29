"""helpers test_checkargs module"""
from unittest.mock import patch
from src.helpers import check_args

VALID_SCRIPT = "graylog_setup.py"
VALID_TOKEN = "A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R8S9T0U1V2W3X4Y5Z6"  # A valid 52-char alphanumeric token
INVALID_TOKEN_SHORT = "SHORTTOKEN123"   # An invalid 13-char alphanumeric token
INVALID_TOKEN_LONG = "LONGTOKENA1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R8S9T0U1V2W3X4Y5Z6" # An invalid 61-char alphanumeric token
INVALID_TOKEN_NONALPHA = "A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R8S9T0U1V2W3X4Y5#$" # An invalid 52-char with non alphanumeric token
VALID_URL = "http://graylog.example.com"   # A placeholder valid URL (actual URL validation isn't done in check_args)
EXPECTED_VALID_OUTPUT = (
    "Checking arguments and validating the inputs.\n"
    "[Done] Checking arguments and validating the inputs.\n\n"
)

def test_check_args_pass_no_verbose_flag(capsys) -> None:
    """helpers test_check_args_pass_no_verbose_flag function"""
    args = [VALID_SCRIPT, VALID_TOKEN, VALID_URL]
    result = check_args(args)
    captured = capsys.readouterr()
    assert len(args) == 4
    assert result[0] == VALID_SCRIPT
    assert result[1] == VALID_TOKEN
    assert result[2] == VALID_URL
    assert isinstance(result[3],str)
    assert captured.out == EXPECTED_VALID_OUTPUT

def test_check_args_pass_true_verbose_flag(capsys) -> None:
    """helpers test_check_args_pass_true_verbose_flag"""
    args = [VALID_SCRIPT, VALID_TOKEN, VALID_URL, "TrUe"]
    result = check_args(args)
    captured = capsys.readouterr()
    assert len(args) == 5
    assert result[0] == VALID_SCRIPT
    assert result[1] == VALID_TOKEN
    assert result[2] == VALID_URL
    assert result[3] is True
    assert isinstance(result[4],str)
    assert captured.out == EXPECTED_VALID_OUTPUT

def test_check_args_pass_false_verbose_flag(capsys) -> None:
    """helpers test_check_args_pass_false_verbose_flag function"""
    args = [VALID_SCRIPT, VALID_TOKEN, VALID_URL, "FaLsE"]
    result = check_args(args)
    captured = capsys.readouterr()
    assert len(args) == 5
    assert result[0] == VALID_SCRIPT
    assert result[1] == VALID_TOKEN
    assert result[2] == VALID_URL
    assert result[3] is False
    assert isinstance(result[4],str)
    assert captured.out == EXPECTED_VALID_OUTPUT

def test_check_args_fail_too_few_arguments() -> None:
    """helpers test_check_args_fail_too_few_arguments function"""
    args = [VALID_SCRIPT, VALID_TOKEN]
    result = check_args(args)
    assert "[ERROR] Wrong number of script arguments. Number of args passed:1" in result

def test_check_args_fail_too_many_arguments() -> None:
    """helpers test_check_args_fail_too_many_arguments function"""
    args = [VALID_SCRIPT, VALID_TOKEN, VALID_URL, "true", "extra"]
    result = check_args(args)
    assert "[ERROR] Wrong number of script arguments. Number of args passed:4" in result

def test_check_args_fail_token_short() -> None:
    """helpers test_check_args_fail_token_short funcion"""
    args = [VALID_SCRIPT, INVALID_TOKEN_SHORT, VALID_URL]
    result = check_args(args)
    assert "[ERROR] Token was wrong length" in result

def test_check_args_fail_token_long() -> None:
    """helpers test_check_args_fail_token_long function"""
    args = [VALID_SCRIPT, INVALID_TOKEN_LONG, VALID_URL]
    result = check_args(args)
    assert "[ERROR] Token was wrong length" in result

def test_check_args_fail_token_non_alphanumeric() -> None:
    """helpers test_check_args_fail_token_non_alphanumeric function"""
    args = [VALID_SCRIPT, INVALID_TOKEN_NONALPHA, VALID_URL]
    result = check_args(args)
    assert "[ERROR] Token had non alphanumeric characters" in result

def test_check_args_fail_bad_verbose_flag_short()-> None:
    """helpers test_check_args_fail_bad_verbose_flag_short function"""
    args = [VALID_SCRIPT, VALID_TOKEN, VALID_URL, "bad"]
    result = check_args(args)
    assert "[ERROR] Optional 3rd argument must be string: true or false." in result

def test_check_args_fail_bad_verbose_flag_long()-> None:
    """helpers test_check_args_fail_bad_verbose_flag_long function"""
    args = [VALID_SCRIPT, VALID_TOKEN, VALID_URL, "badflag"]
    result = check_args(args)
    assert "[ERROR] Optional 3rd argument must be string: true or false." in result

def test_check_args_fail_verbose_argument()-> None:
    """helpers test_check_args_fail_verbose_argument function"""
    args = [VALID_SCRIPT, VALID_TOKEN, VALID_URL, "maybe"]
    result = check_args(args)
    assert "[ERROR] Optional 3rd argument must be string: true or false" in result

def test_check_args_fail_invalid_verbose_type()-> None:
    """helpers test_check_args_fail_invalid_verbose_type function"""
    args = [VALID_SCRIPT, VALID_TOKEN, VALID_URL, 12345]  # Not a string
    result = check_args(args)
    assert "[ERROR] Optional 3rd argument must be string: true or false" in result

def test_os_error_handling()-> None:
    """helpers test_os_error_handling function"""
    with patch('os.getcwd', side_effect=OSError("Mocked OS error")), patch('sys.exit') as mock_exit:
        args = [VALID_SCRIPT, VALID_TOKEN, VALID_URL, "FaLsE"]
        check_args(args)
        mock_exit.assert_called_once_with(1)  # Check that sys.exit(1) was called
