"""Enums for schema.

NOTE: jsonschema/rest is still source of truth,
regardless of what this module includes.
"""

import enum
import logging

LOGGER = logging.getLogger(__name__)


class TaskforcePhase(enum.StrEnum):  # attrs are str sub-types! (no `.value` needed)
    """The enum values used for 'phase'."""

    PRE_MQ_ACTIVATOR = "pre-mq-activation"
    PRE_LAUNCH = "pre-launch"
    PENDING_STARTER = "pending-starter"
    CONDOR_SUBMIT = "condor-submit"
    PENDING_STOPPER = "pending-stopper"
    CONDOR_RM = "condor-rm"
    CONDOR_COMPLETE = "condor-complete"


ENDING_OR_FINISHED_TASKFORCE_PHASES = [
    # these indicate the taskforce is ending or finished
    TaskforcePhase.PENDING_STOPPER,
    TaskforcePhase.CONDOR_RM,
    TaskforcePhase.CONDOR_COMPLETE,
]
