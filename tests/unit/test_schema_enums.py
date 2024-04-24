"""Test schema.enums.py."""


import copy
import logging

import jsonschema

from wms import config, schema

LOGGER = logging.getLogger(__name__)


def test_tmsaction() -> None:
    """Validate the TaskforcePhase attrs with the jsonschema."""
    spec = copy.deepcopy(config.MONGO_COLLECTION_JSONSCHEMA_SPECS["Taskforce"])
    spec["required"] = []

    for attr in [*schema.enums.TaskforcePhase]:
        print(f"validating: {attr}")
        jsonschema.validate({"phase": attr}, spec)
