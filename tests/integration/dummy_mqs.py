"""A dummy MQS server for testing."""

import os
import time
from typing import Any

from flask import Flask, jsonify, request

app = Flask(__name__)

DONT_CALL_IT_A_DB: dict[str, Any] = {}


@app.route("/v0/mqs/workflows/<workflow_id>/mq-group/reservation", methods=["POST"])
def dummy_mq_group_reservation_post(workflow_id: str):
    mqgroup_id = f"test-mq-group-{workflow_id}"
    now = time.time()

    resp = {
        "mqgroup": {
            "mqgroup_id": mqgroup_id,
            "timestamp": now,
            "criteria": {},  # updated on activation
        },
        "mqprofiles": [
            {
                "mqid": f"123{alias}",
                "mqgroup_id": mqgroup_id,
                "timestamp": now,
                "alias": alias,
                "is_public": alias in request.get_json()["public"],
                "is_activated": False,
                "auth_token": None,
                "broker_type": None,
                "broker_address": None,
            }
            for alias in request.get_json()["queue_aliases"]
        ],
    }

    DONT_CALL_IT_A_DB[workflow_id] = resp
    return jsonify(resp)


@app.route("/v0/mqs/workflows/<workflow_id>/mq-group/activation", methods=["POST"])
def dummy_mq_group_activation_post(workflow_id: str):
    # in the real mqs, there's a bunch of db logic, etc.

    stored = DONT_CALL_IT_A_DB[workflow_id]
    for mqprofile in stored["mqprofiles"]:
        mqprofile["is_activated"] = True
        mqprofile["auth_token"] = "DUMMY_TOKEN"
        mqprofile["broker_type"] = "DUMMY_BROKER_TYPE"
        mqprofile["broker_address"] = "DUMMY_BROKER_ADDRESS"

    return jsonify(stored)


if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=int(os.environ["MQS_ADDRESS"].split(":")[-1]),
    )
