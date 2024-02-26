"""set_all_nested.py."""


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
