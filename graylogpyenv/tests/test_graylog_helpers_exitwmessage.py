import pytest
from src.graylog_helpers import exit_with_message

def test_exit_wmessage_pass_output_returncode(capsys):
    with pytest.raises(SystemExit) as e:
        exit_with_message("Test message from exit with message",2)
    captured = capsys.readouterr()
    assert captured.out == "Test message from exit with message\n"
    assert e.value.code == 2
