from itertools import zip_longest
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from project.core.type_alias import JsonDct
from project.core.type_alias import JsonLst

# Value used in assert-functions to check that only key must be presented in response
AnyValue = object()


def assert_response_contains_dict(resp_data: JsonDct, expected: dict[str, Any] | None) -> None:
    """Assert that response data contains all tags which we expect."""
    if expected is AnyValue:
        return
    expected = expected or {}

    if len(resp_data) != len(expected):
        raise AssertionError(f"Response contains invalid data: {resp_data} (expected: {expected})")

    for key, expected_val in expected.items():
        res_val = resp_data[key]
        if isinstance(res_val, dict):
            assert_response_contains_dict(res_val, expected_val)
            continue
        if expected_val is AnyValue:
            continue
        if isinstance(res_val, list) and res_val:
            one_item = res_val[0]
            if isinstance(one_item, (int, bool, str, float, UUID)):
                res_val = sorted(res_val)
                expected_val = sorted(expected_val)
            elif isinstance(one_item, BaseModel):
                res_val = sorted(res_val, key=lambda o: id(o))
                expected_val = sorted(expected_val, key=lambda o: id(o))

        assert res_val == expected_val, (
            f"Response contains invalid value in '{key}' "
            f"(expected: {expected_val} (type:{type(expected_val)}), actual: {res_val} (type:{type(res_val)}))"
        )


def assert_response_list_equals(resp_data: JsonLst, expected: list[dict[str, Any]]) -> None:
    """Assert that list response equals to expected."""
    if not expected:
        assert not resp_data, f"Expected empty list, but responded with {resp_data}"
        return

    sort_key = "id" if "id" in expected[0].keys() else list(expected[0].keys())[0]

    def sort_func(item):
        return item[sort_key]

    sorted_resp = sorted(resp_data, key=sort_func)
    sorted_expected = sorted(expected, key=sort_func)

    for resp_dct, expected_dct in zip_longest(sorted_resp, sorted_expected, fillvalue=dict()):  # type: ignore
        assert_dicts_equal(resp_dct, expected_dct)


def assert_dicts_equal(resp_data: JsonDct, expected: dict[str, Any]) -> None:
    """Assert that response data equals to expectations."""
    assert sorted(resp_data.keys()) == sorted(expected.keys()), "Keys are not equal"
    assert_response_contains_dict(resp_data, expected)


def assert_jrpc_response_has_error(resp_data: JsonDct, expected: dict[str, Any]) -> None:
    """Asserts that JSON RPC response contains expected error.

    Works with 2 variants of errors:
        * the only one, which is instance of `fastapi_jsonrpc.InternalError`
        * multiple errors in result stored in resp_data['error']['data']['errors']
    """
    error_content = resp_data["error"]
    if error_content.get("data"):
        actual_resp = error_content["data"]["errors"]
    else:
        actual_resp = [error_content]

    if not any((err_dct == expected for err_dct in actual_resp)):
        raise AssertionError(f"Response doesn't contain expected error (expected: {expected}, actual: {actual_resp})")
