"""Enums for schema.

NOTE: jsonschema/rest is still source of truth,
regardless of what this module includes.
"""


import enum
import logging

LOGGER = logging.getLogger(__name__)


class TMSAction(enum.StrEnum):  # attrs are str subclass types! (no `.value` needed)
    """The enum values used for 'tms_most_recent_action'."""

    PRE_TMS = "pre-tms"
    PENDING_STARTER = "pending-starter"
    CONDOR_SUBMIT = "condor-submit"
    PENDING_STOPPER = "pending-stopper"
    CONDOR_RM = "condor-rm"
