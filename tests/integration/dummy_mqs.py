"""A dummy MQS server for testing."""


import os
import time

from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/mq-group", methods=["POST"])
def dummy_mq_group_post():
    mqgroup_id = "test-mq-group"
    now = int(time.time())

    return jsonify(
        dict(
            mqgroup=dict(
                mqgroup_id=mqgroup_id,
                timestamp=now,
                criteria={},
            ),
            mqprofiles=[
                dict(
                    mqid=f"t{i}",
                    mqgroup_id=mqgroup_id,
                    timestamp=now,
                    nickname=f"mq-{mqgroup_id}-{i}",
                )
                for i in range(2)
            ],
        )
    )


if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=int(os.environ["MQS_ADDRESS"].split(":")[-1]),
    )
