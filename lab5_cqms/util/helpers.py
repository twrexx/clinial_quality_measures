"""
File to implement shared utility functions.

Feel free to expand on these - none are explicitly required, though it'll be useful
to prevent re-implementing logic across multiple CQM classes.
"""

import re
from datetime import datetime
from typing import Any

import arrow


def get_datediff_in_years(date_a: str | datetime, date_b: str | datetime) -> float:
    """
    Get days since date_a relative to date_b (i.e. date_b - date_a).

    I.e. the result is positive if date_b occurs after date_a, otherwise negative (barring 0.0)
    """
    if isinstance(date_a, str):
        date_a = arrow.get(date_a).datetime
    if isinstance(date_b, str):
        date_b = arrow.get(date_b).datetime
    delta = date_b - date_a
    return delta.days / 365.0


def date_is_within_date_range(
    ref_date: str, start: str | datetime, end: str | datetime
) -> bool:
    """
    Returns True if ref_date falls between start and end
    """
    years_since_start = get_datediff_in_years(
        ref_date, start
    )  # Negative if ref_date is after start
    years_since_end = get_datediff_in_years(ref_date, end)
    return years_since_start <= 0 and years_since_end >= 0


def get_resource_sublist(
    resource_list: list[dict[str, Any]],
    pid_set: set[str],
    pid_reference_key="subject.reference",
) -> list[dict[str, Any]]:
    """
    Returns the subset of resources in `resource_list` that contain a patient ID in `pid_set`.

    Checks specifically in the field denoted in `pid_reference_key`.
    """
    return [
        r
        for r in resource_list
        if get_reference_id_from_resource(r, pid_reference_key) in pid_set
    ]


def get_reference_id_from_resource(
    r: dict[str, Any], key: str = "subject.reference"
) -> str:
    """
    Gets-into the specified `key` and pulls the id

    Assumes data is well-formed in the exact format: "resourceType/id"
    """
    return nested_get(r, key).split("/")[1]


def nested_get(source: dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Expects `.`-delimited string and tries to get the item in the dict.

    If the dict contains an array, the correct index is expected, e.g. for a dict d:
        d.a.b[0]
      will try d['a']['b'][0], where b should be an array with at least 1 item.
    """
    res = source
    for key_part in key.split("."):
        res = _single_get(res, key_part)
        if res is None:
            break
    return res if res is not None else default


REGEX_INDEX = re.compile(r"(.*)\[(-?\d+)\]$")


def _single_get(source: dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Gets single item, supports int indexing, e.g. `someKey[0]`
    """
    if key.endswith("]"):
        if match := REGEX_INDEX.fullmatch(key):
            key_part = match.group(1)
            index_part = match.group(2)
            values = source.get(key_part, [])
            try:
                return values[int(index_part)]
            except IndexError:
                return None
    return source.get(key, default)


"""
Include custom helper functions below!
"""
