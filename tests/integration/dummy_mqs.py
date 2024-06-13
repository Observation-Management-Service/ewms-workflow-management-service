"""A dummy MQS server for testing."""

import os
import time

from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/v0/mqs/workflows/<workflow_id>/mq-group/reservation", methods=["POST"])
def dummy_mq_group_reservation_post(workflow_id: int):
    mqgroup_id = f"test-mq-group-{workflow_id}"
    now = time.time()

    return jsonify(
        {
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
                }
                for alias in request.get_json()["queue_aliases"]
            ],
        }
    )


@app.route("/v0/mqs/workflows/<workflow_id>/mq-group/activation", methods=["POST"])
def dummy_mq_group_activation_post(workflow_id: int):
    # in the real mqs, there's a bunch of db logic, etc.
    return jsonify({"activated": True})


if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=int(os.environ["MQS_ADDRESS"].split(":")[-1]),
    )
