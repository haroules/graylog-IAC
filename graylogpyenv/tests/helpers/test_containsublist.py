"""Module:tests.helpers.test_containsublist"""
import pytest

from src.helpers import contains_sublist
from tests.common.test_common import shared_asserts

def test_contains_sublist_pass_valid_list() -> None:
    """Function:test_contains_sublist_pass_valid_list"""
    sub_list = ["item one", "item two"]
    main_list = ["item three", "item one", "item two"]
    result = contains_sublist(sub_list,main_list)
    assert result is True

def test_contains_sublist_fail_invalid_item(capsys) -> None:
    """Function:test_contains_sublist_fail_invalid_item"""
    with pytest.raises(SystemExit) as e:
        sub_list = "item one"
        main_list = ["item three", "item one", "item two"]
        contains_sublist(sub_list,main_list)
    captured = capsys.readouterr()
    expected_output = "[ERROR] One or more items passed to contains_sublist is not a list\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_contains_sublist_fail_sublist_notinlist() -> None:
    """Function:test_contains_sublist_fail_sublist_notinlist"""
    sub_list = ["item four"]
    main_list = ["item three", "item one", "item two"]
    result = contains_sublist(sub_list,main_list)
    assert result is False
