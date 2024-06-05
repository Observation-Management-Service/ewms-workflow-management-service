#!/bin/bash
set -ex

# meant to be copy-pasted into terminal as one-liner, with tokens replaced

export EWMS_PILOT_BROKER_ADDRESS="XXX"  &&  export KEYCLOAK_CLIENT_ID_BROKER="ewms-rabbitmq" &&  export KEYCLOAK_CLIENT_SECRET_BROKER=$(echo YYY | base64 --decode)  &&  python3 request_workflow.py --pilot-cvmfs-image-tag A.B.C
