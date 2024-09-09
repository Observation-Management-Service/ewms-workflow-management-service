"""Utils for REST routes."""
import json
import logging

from .. import config

LOGGER = logging.getLogger(__name__)


def add_values_to_pilot_config(task_input: dict) -> dict:
    """Add values (default and detected) to the pilot config dictionary."""
    pilot_config = task_input.get("pilot_config", {})

    # add to env vars
    if "environment" not in pilot_config:
        pilot_config["environment"] = {}
    pilot_config["environment"].update(
        {
            "EWMS_PILOT_TASK_IMAGE": task_input["task_image"],
            "EWMS_PILOT_TASK_ARGS": task_input["task_args"],
            "EWMS_PILOT_TASK_ENV_JSON": json.dumps(task_input["task_env"]),
        }
    )

    # attach defaults
    return {
        "image": config.get_pilot_image(pilot_config.get("image", "latest")),
        "environment": pilot_config["environment"],
        "input_files": pilot_config.get("input_files", []),
    }
