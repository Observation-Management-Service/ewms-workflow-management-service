"""modify_db_schemas.py."""


import json
import logging
import pathlib

LOGGER = logging.getLogger(__name__)


def main() -> None:
    """Main."""

    for fpath in pathlib.Path(".").iterdir():
        # find 'responses' keys, and override/add 400
        with open(fpath) as f:
            spec = json.load(f)
        spec["required"] = list(spec["properties"].keys())
        spec["additionalProperties"] = False

        # format neatly
        with open(fpath, "w") as f:
            json.dump(spec, f, indent=4)
        with open(fpath, "a") as f:  # else json.dump removes trailing newline
            f.write("\n")


if __name__ == "__main__":
    main()
