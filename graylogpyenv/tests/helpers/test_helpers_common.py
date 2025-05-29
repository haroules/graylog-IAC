"""helpers test_common module"""
import pytest

from src.helpers import remove_sublists
from src.helpers import usage

def test_clean_usage_output(capsys) -> None:
    """helpers test_clean_usage_output function"""
    usage(["graylog_clean.py"])
    captured = capsys.readouterr()
    expected_output = (
        "CAREFUL! Running this will delete all data on your graylog instance.\n"
        "Usage: graylog_clean.py <admin token> <url> <verbose>\n"
        "  -Admin token and url are required, verbose defaults to True if not set (to False).\n"
        "  -Token should be 52 alpha-numeric characters.\n"
        "  -URL should be of the form http(s)://host|ip:port.\n"
        "  -Setting verbose to False will supress output.\n\n"
    )
    assert captured.out == expected_output

def test_setup_usage_output(capsys) -> None:
    """helpers test_setup_usage_output function"""
    usage(["graylog_setup.py"])
    captured = capsys.readouterr()
    expected_output = (
        "Usage: graylog_setup.py <admin token> <url> <verbose>\n"
        "  -Admin token and url are required, verbose defaults to True if not set (to False).\n"
        "  -Token should be 52 alpha-numeric characters.\n"
        "  -URL should be of the form http(s)://host|ip:port.\n"
        "  -Setting verbose to False will supress output.\n\n"
    )
    assert captured.out == expected_output

def test_verify_usage_output(capsys) -> None:
    """helpers test_verify_usage_output function"""
    usage(["graylog_verify.py"])
    captured = capsys.readouterr()
    expected_output = (
        "Usage: graylog_verify.py <verbose>\n"
        "  -Verbose defaults to True if not set (to False).\n"
        "  -Setting verbose to False will supress output.\n\n"
    )
    assert captured.out == expected_output

def test_remove_sublists_pass() -> None:
    """helpers test_remove_sublists_pass function"""
    sub_list = ["item one", "item two"]
    main_list = ["item one", "item two", "item_three", "item_four"]
    result = remove_sublists(main_list,sub_list)
    assert result == ["item_three", "item_four"]

def test_remove_sublists_fail_no_elements_to_remove(capsys) -> None:
    """helpers test_remove_sublists_fail_no_elements_to_remove function"""
    sub_list = ["item one", "item two"]
    main_list = ["item one", "item two"]
    with pytest.raises(SystemExit) as e:
        remove_sublists(main_list,sub_list)
    captured = capsys.readouterr()
    assert captured.out == "[ERROR] in remove sublists, main list doesn't have elements to remove\n"
    assert e.value.code == 1

def test_remove_sublists_fail_nothing_removed(capsys) -> None:
    """helpers test_remove_sublists_fail_nothing_removed function"""
    sub_list = ["item one", "item two"]
    main_list = ["item three", "item four", "item five"]
    with pytest.raises(SystemExit) as e:
        remove_sublists(main_list,sub_list)
    captured = capsys.readouterr()
    assert captured.out == "[ERROR] in remove sublists, new list doesn't have required number of changes\n"
    assert e.value.code == 1
