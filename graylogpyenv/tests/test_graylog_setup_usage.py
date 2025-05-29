import pytest
from src.graylog_setup import usage

def test_usage_output(capsys):
    with pytest.raises(SystemExit) as e:
        usage()
    captured = capsys.readouterr()
    expected_output = (
        "Usage: graylog-setup.py <admin token> <url> <verbose>\n"
        "\t-Admin token and url are required, verbose defaults to True if not set (to False).\n"
        "\t-Token should be 52 alpha-numeric characters.\n"
        "\t-URL should be of the form http(s)://host|ip:port .\n"
        "\t-Setting verbose to False will supress output.\n"
    )
    assert captured.out == expected_output
    assert e.value.code == 1
