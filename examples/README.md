# Examples

These example script(s) serve as a starting place to base future more functionally advanced scripts upon. They also
serve as an in-production system testing, with an active EWMS cluster and TMS.

## How to Run

Replace the placeholder values, then run this as a one-liner:

```bash
export EWMS_PILOT_BROKER_ADDRESS="XXX"  &&  export KEYCLOAK_CLIENT_ID_BROKER="ewms-rabbitmq" &&  export KEYCLOAK_CLIENT_SECRET_BROKER=$(echo YYY | base64 --decode)  &&  python3 request_workflow.py --pilot-cvmfs-image-tag A.B.C
```
