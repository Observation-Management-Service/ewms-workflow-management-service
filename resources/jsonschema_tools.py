"""jsonschema_strict_utils.py."""


import logging
from typing import Callable

LOGGER = logging.getLogger(__name__)


def set_all_nested(
    spec: dict,
    setter: Callable[[dict, str], None],
    if_this: Callable[[dict, str], bool],
) -> dict:
    """Call 'setter' for every key where 'if_this' is True."""

    def settle_nested_subdict_one_at_a_time(subdict: dict):
        """Calling repeatedly will complete the settling.

        Will return without error if nothing was changed.
        """
        for key, val in subdict.items():
            if if_this(subdict, key):
                setter(subdict, key)
                raise Exception("dict may have changed (did not check prev value)")
            elif isinstance(val, dict):
                settle_nested_subdict_one_at_a_time(val)

    while True:
        try:
            settle_nested_subdict_one_at_a_time(spec)
        except:  # noqa: E722
            continue
        break

    return spec


def all_properties_required(spec: dict) -> None:
    """Find "properties" keys, then set their "required" keys."""

    def set_requireds(d, k):
        d["required"] = list(d["properties"].keys())

    set_all_nested(
        spec,
        set_requireds,
        lambda d, k: k == "properties",
    )


def array_min_items(spec: dict, default: int) -> None:
    """Set 'minItems' for all arrays (that don't already have it)."""

    def set_minItems(d, k):
        d.update({"minItems": default})

    set_all_nested(
        spec,
        set_minItems,
        lambda d, k: k == "type" and d[k] == "array" and "minItems" not in d,
    )


def additional_properties_default(spec: dict, default: bool) -> None:
    """Set "additionalProperties" keys."""

    # NOTE: do this last since it affects above modifications

    def set_additionalProperties(d, k):
        d["additionalProperties"] = default

    set_all_nested(
        spec,
        set_additionalProperties,
        lambda d, k: k == "properties" and "additionalProperties" not in d,
    )


def properties_minimum(spec: dict, default: int) -> None:
    """Set 'minProperties' for all arrays (that don't already have it)."""

    def set_minProperties(d, k):
        d.update({"minProperties": default})

    set_all_nested(
        spec,
        set_minProperties,
        lambda d, k: (
            k == "type"
            and d[k] == "object"
            and "minProperties" not in d  # don't override
            #
            and "properties" not in d  # AKA it's completely open object
            and d.get("additionalProperties") is not False  # just in case
        ),
    )
