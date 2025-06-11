"""tests.helpers test_exit_wmessage module"""
import pytest

from src.helpers import exit_with_message
from tests.common.test_common import shared_asserts

def test_exit_wmessage_pass_output_returncode(capsys) -> None:
    """tests.helpers.test_exit_wmessage_pass_output_returncode function"""
    with pytest.raises(SystemExit) as e:
        exit_with_message("Test message from exit with message",1)
    captured = capsys.readouterr()
    expected_output = "Test message from exit with message\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
