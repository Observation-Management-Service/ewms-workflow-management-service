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

        jsonschema_tools.override_all_properties_required(spec)
        jsonschema_tools.set_default_array_minitems(spec, 0)
        jsonschema_tools.set_default_additionalproperties(spec, False)
        jsonschema_tools.set_default_minproperties(spec, 0)

        # format neatly
        with open(fpath, "w") as f:
            json.dump(spec, f, indent=4)
        with open(fpath, "a") as f:  # else json.dump removes trailing newline
            f.write("\n")


if __name__ == "__main__":
    main()
