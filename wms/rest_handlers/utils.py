"""Utils for REST routes."""

import logging

from .. import config

LOGGER = logging.getLogger(__name__)


def add_values_to_pilot_config(task_input: dict) -> dict:
    """Add values (default and detected) to the pilot config dictionary."""
    dicto = task_input.get("pilot_config", {})

    # add to env vars
    if "environment" not in dicto:
        dicto["environment"] = {}
    dicto["environment"].update(
        {
            "EWMS_PILOT_TASK_IMAGE": task_input["task_image"],
            "EWMS_PILOT_TASK_ARGS": task_input["task_args"],
        }
    )

    # attach defaults
    return {
        "image": config.get_pilot_image(dicto.get("image", "latest")),
        "environment": dicto["environment"],
        "input_files": dicto.get("input_files", []),
    }
