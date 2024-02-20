"""modify_rest_path_schemas.py."""


import json
import logging
import pathlib
import re

from set_all_nested import set_all_nested

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

NEW_404 = {
    "description": "not found",
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

        # find "responses" keys, then set their "404" keys
        def set_responses_404(d, k):
            d["responses"].update({"404": NEW_404})

        # Using re.findall() to extract strings inside {}
        # ex: example.{id}.json
        if re.findall(r"\{([^/{}]+)\}", str(fpath)):
            set_all_nested(
                spec,
                set_responses_404,
                lambda d, k: k == "responses" and d["responses"].get("404") != NEW_404,
            )

        # set 'minItems' for all arrays (that don't already have it)
        def set_array_minimum(d, k):
            d.update({"minItems": 0})

        set_all_nested(
            spec,
            set_array_minimum,
            lambda d, k: k == "type" and d[k] == "array" and "minItems" not in d,
        )

        # format neatly
        with open(fpath, "w") as f:
            json.dump(spec, f, indent=4)
        with open(fpath, "a") as f:  # else json.dump removes trailing newline
            f.write("\n")


if __name__ == "__main__":
    main()
