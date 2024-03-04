"""modify_db_schemas.py."""


import json
import logging
import pathlib

import jsonschema_tools

LOGGER = logging.getLogger(__name__)


def main() -> None:
    """Main."""

    for fpath in pathlib.Path(".").iterdir():
        with open(fpath) as f:
            spec = json.load(f)

        jsonschema_tools.all_properties_required(spec)
        jsonschema_tools.array_min_items(spec, 0)
        jsonschema_tools.additional_properties_default(spec, False)
        jsonschema_tools.properties_minimum(spec, 0)

        # format neatly
        with open(fpath, "w") as f:
            json.dump(spec, f, indent=4)
        with open(fpath, "a") as f:  # else json.dump removes trailing newline
            f.write("\n")


if __name__ == "__main__":
    main()
