"""helpers test_exit_wmessage module"""
import pytest

from src.helpers import exit_with_message

def test_exit_wmessage_pass_output_returncode(capsys) -> None:
    """helpers test_exit_wmessage_pass_output_returncode function"""
    with pytest.raises(SystemExit) as e:
        exit_with_message("Test message from exit with message",2)
    captured = capsys.readouterr()
    assert captured.out == "Test message from exit with message\n"
    assert e.value.code == 2
