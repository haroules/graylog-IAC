"""Module:tests.helpers.test_common"""
import pytest

from src.helpers import remove_sublists
from src.helpers import usage
from tests.common.test_common import shared_asserts

def test_clean_usage_output(capsys) -> None:
    """Function:test_clean_usage_output"""
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
    """Function:test_setup_usage_output"""
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
    """Function:test_verify_usage_output"""
    usage(["graylog_verify.py"])
    captured = capsys.readouterr()
    expected_output = (
        "Usage: graylog_verify.py <verbose>\n"
        "  -Verbose defaults to True if not set (to False).\n"
        "  -Setting verbose to False will supress output.\n\n"
    )
    assert captured.out == expected_output

def test_remove_sublists_pass() -> None:
    """Function:test_remove_sublists_pass"""
    sub_list = ["item one", "item two"]
    main_list = ["item one", "item two", "item_three", "item_four"]
    result = remove_sublists(main_list,sub_list)
    assert result == ["item_three", "item_four"]

def test_remove_sublists_fail_no_elements_to_remove(capsys) -> None:
    """Function:test_remove_sublists_fail_no_elements_to_remove"""
    sub_list = ["item one", "item two"]
    main_list = ["item one", "item two"]
    with pytest.raises(SystemExit) as e:
        remove_sublists(main_list,sub_list)
    captured = capsys.readouterr()
    expected_output = "[ERROR] in remove sublists, main list doesn't have elements to remove\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_remove_sublists_fail_nothing_removed(capsys) -> None:
    """Function:test_remove_sublists_fail_nothing_removed"""
    sub_list = ["item one", "item two"]
    main_list = ["item three", "item four", "item five"]
    with pytest.raises(SystemExit) as e:
        remove_sublists(main_list,sub_list)
    captured = capsys.readouterr()
    expected_output = "[ERROR] in remove sublists, new list doesn't have required number of changes\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
