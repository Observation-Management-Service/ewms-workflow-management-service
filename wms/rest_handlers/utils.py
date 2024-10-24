"""Utils for REST routes."""

import json
import logging

from .. import config

LOGGER = logging.getLogger(__name__)


async def add_values_to_pilot_config(task_input: dict) -> dict:
    """Add values (default and detected) to the pilot config dictionary."""
    pilot_config = task_input.get("pilot_config", {})

    # add to env vars
    if "environment" not in pilot_config:
        pilot_config["environment"] = {}
    # -> required attrs
    pilot_config["environment"].update(
        {
            "EWMS_PILOT_TASK_IMAGE": task_input["task_image"],
            "EWMS_PILOT_TASK_ARGS": task_input["task_args"],
        }
    )
    # -> optional attrs
    if val := task_input.get("task_env"):
        pilot_config["environment"]["EWMS_PILOT_TASK_ENV_JSON"] = json.dumps(val)
    if val := task_input.get("init_image"):
        pilot_config["environment"]["EWMS_PILOT_INIT_IMAGE"] = val
    if val := task_input.get("init_args"):
        pilot_config["environment"]["EWMS_PILOT_INIT_ARGS"] = val
    if val := task_input.get("init_env"):
        pilot_config["environment"]["EWMS_PILOT_INIT_ENV_JSON"] = json.dumps(val)

    # attach defaults
    return {
        "tag": await config.get_pilot_tag(pilot_config.get("tag", "latest")),
        "environment": pilot_config["environment"],
        "input_files": pilot_config.get("input_files", []),
    }
