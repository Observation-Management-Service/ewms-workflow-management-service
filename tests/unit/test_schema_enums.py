"""Test schema.enums.py."""

import copy
import logging

import jsonschema

from wms import schema
from wms.database.utils import TASKFORCES_COLL_NAME, get_jsonschema_spec

LOGGER = logging.getLogger(__name__)


def test_tmsaction() -> None:
    """Validate the TaskforcePhase attrs with the jsonschema."""
    spec = copy.deepcopy(get_jsonschema_spec(TASKFORCES_COLL_NAME))
    spec["required"] = []

    for attr in [*schema.enums.TaskforcePhase]:
        print(f"validating: {attr}")
        jsonschema.validate({"phase": attr}, spec)
