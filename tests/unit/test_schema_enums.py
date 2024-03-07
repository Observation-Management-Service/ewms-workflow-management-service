"""Test schema.enums.py."""


import copy
import logging

import jsonschema
from wms import config, schema

LOGGER = logging.getLogger(__name__)


def test_tmsaction() -> None:
    """Validate the TMSAction attrs with the jsonschema."""
    spec = copy.deepcopy(config.MONGO_COLLECTION_JSONSCHEMA_SPECS["Taskforce"])
    spec["required"] = []

    for attr in [e.value for e in schema.enums.TMSAction]:
        print(f"validating: {attr}")
        jsonschema.validate({"tms_most_recent_action": attr}, spec)
