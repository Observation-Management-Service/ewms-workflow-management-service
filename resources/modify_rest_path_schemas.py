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


def settle_nested_dictkeyval_one_at_a_time(
    d: dict,
    setter: Callable,
    if_this: Callable,
):
    """Calling repeatedly will complete the settling.

    Will return without error if nothing was changed.
    """
    for k, v in d.items():
        if if_this(d, k):
            setter(d, k)
            raise Exception("dict may have changed (did not check prev value)")
        elif isinstance(v, dict):
            settle_nested_dictkeyval_one_at_a_time(v, setter, if_this)


def main() -> None:
    """Main."""

    # GO!
    for fpath in pathlib.Path(".").iterdir():
        with open(fpath) as f:
            spec = json.load(f)

        # set "additionalProperties" keys
        def set_additionalProperties(d, k):
            d["additionalProperties"] = False

        while True:
            try:
                settle_nested_dictkeyval_one_at_a_time(
                    spec,
                    set_additionalProperties,
                    lambda d, k: k == "properties" and "additionalProperties" not in d,
                )
            except:
                continue
            break

        # find "responses" keys, then set their "400" keys
        def set_responses_400(d, k):
            d["responses"].update({"400": NEW_400})

        while True:
            try:
                settle_nested_dictkeyval_one_at_a_time(
                    spec,
                    set_responses_400,
                    lambda d, k: k == "responses"
                    and d["responses"].get("400") != NEW_400,
                )
            except:  # noqa: E722
                continue
            break

        # format neatly
        with open(fpath, "w") as f:
            json.dump(spec, f, indent=4)
        with open(fpath, "a") as f:  # else json.dump removes trailing newline
            f.write("\n")


if __name__ == "__main__":
    main()
