"""modify_rest_path_schemas.py."""


import json
import logging
import pathlib
from typing import Callable

LOGGER = logging.getLogger(__name__)

NEW_400 = {
    "description": "invalid request arguments",
    "content": {
        "application/json": {
            "schema": {
                "type": "object",
                "properties": {
                    "code": {"description": "http error code", "type": "integer"},
                    "error": {"description": "http error reason", "type": "string"},
                },
                "required": ["code", "error"],
            }
        }
    },
}


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


def main() -> None:
    """Main."""

    # GO!
    for fpath in pathlib.Path(".").iterdir():
        with open(fpath) as f:
            spec = json.load(f)

        # set "additionalProperties" keys
        def set_additionalProperties(d, k):
            d["additionalProperties"] = False

        set_all_nested(
            spec,
            set_additionalProperties,
            lambda d, k: k == "properties" and "additionalProperties" not in d,
        )

        # find "responses" keys, then set their "400" keys
        def set_responses_400(d, k):
            d["responses"].update({"400": NEW_400})

        set_all_nested(
            spec,
            set_responses_400,
            lambda d, k: k == "responses" and d["responses"].get("400") != NEW_400,
        )

        # format neatly
        with open(fpath, "w") as f:
            json.dump(spec, f, indent=4)
        with open(fpath, "a") as f:  # else json.dump removes trailing newline
            f.write("\n")


if __name__ == "__main__":
    main()
