"""Test schema.enums.py."""

import logging

import jsonschema

from wms import schema
from wms.database.utils import TASKFORCES_COLL_NAME, get_jsonschema_subspec_from_openapi

LOGGER = logging.getLogger(__name__)


def test_tmsaction() -> None:
    """Validate the TaskforcePhase attrs with the jsonschema."""
    spec = get_jsonschema_subspec_from_openapi(
        TASKFORCES_COLL_NAME.removesuffix("Coll") + "Object"
    )
    spec["required"] = []

    for attr in [*schema.enums.TaskforcePhase]:
        print(f"validating: {attr}")
        jsonschema.validate({"phase": attr}, spec)
