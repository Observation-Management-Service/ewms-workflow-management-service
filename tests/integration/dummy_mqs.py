"""A dummy MQS server for testing."""

import os
import time

from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/mq-group/reserve", methods=["POST"])
def dummy_mq_group_reserve_post():
    mqgroup_id = "test-mq-group"
    now = time.time()

    return jsonify(
        dict(
            mqgroup=dict(
                mqgroup_id=mqgroup_id,
                timestamp=now,
                criteria={},  # updated on activation
            ),
            mqprofiles=[
                dict(
                    mqid=f"123{alias}",
                    mqgroup_id=mqgroup_id,
                    timestamp=now,
                    alias=alias,
                    is_public=alias in request.get_json()["public"],
                    is_activated=False,
                )
                for alias in request.get_json()["queue_aliases"]
            ],
        )
    )


if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=int(os.environ["MQS_ADDRESS"].split(":")[-1]),
    )
