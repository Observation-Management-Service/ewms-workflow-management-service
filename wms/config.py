"""Config settings."""

import dataclasses as dc
import json
import logging
import re
from pathlib import Path
from typing import Any

import aiocache  # type: ignore[import-untyped]
import jsonschema
import openapi_core
from jsonschema_path import SchemaPath
from openapi_spec_validator import validate
from openapi_spec_validator.readers import read_from_filename
from rest_tools.client import RestClient
from tornado import web
from wipac_dev_tools import from_environment_as_dataclass, logging_tools

LOGGER = logging.getLogger(__name__)

DB_JSONSCHEMA_DIR = Path(__file__).parent / "schema/db"
REST_OPENAPI_SPEC_FPATH = Path(__file__).parent / "schema/rest/openapi_compiled.json"

MQS_RETRY_AT_TS_DEFAULT_VALUE = float("inf")
TASK_MQ_ACTIVATOR_SHORTEST_SLEEP = 1

DEFAULT_WORKFLOW_PRIORITY = 50
MAX_WORKFLOW_PRIORITY = 100  # any value over this is used to accelerate launch

MQS_URL_V_PREFIX = "v1"

# --------------------------------------------------------------------------------------


@dc.dataclass(frozen=True)
class EnvConfig:
    """Environment variables."""

    # pylint:disable=invalid-name
    MONGODB_HOST: str  # "localhost"
    MONGODB_PORT: int  # 27017
    REST_HOST: str  # "localhost"
    REST_PORT: int  # 8080

    MQS_ADDRESS: str
    MQS_TOKEN_URL: str = ""  # needed in prod
    MQS_CLIENT_ID: str = ""  # ''
    MQS_CLIENT_SECRET: str = ""  # ''

    AUTH_AUDIENCE: str = ""
    AUTH_OPENID_URL: str = ""
    MONGODB_AUTH_PASS: str = ""  # empty means no authentication required
    MONGODB_AUTH_USER: str = ""  # None means required to specify

    CI: bool = False  # github actions sets this to 'true'
    LOG_LEVEL: str = "DEBUG"
    LOG_LEVEL_THIRD_PARTY: str = "INFO"
    LOG_LEVEL_REST_TOOLS: str = "DEBUG"

    USER_REST_MONGO_QUERY_LIMIT: int = 100

    WORKFLOW_MQ_ACTIVATOR_DELAY: int = 15
    WORKFLOW_MQ_ACTIVATOR_MQS_RETRY_WAIT: int = 60
    TASKFORCE_LAUNCH_CONTROL_DELAY: int = 1

    TMS_ACTION_RETRIES: int = 2  # 2 retries -> 3 total attempts


ENV = from_environment_as_dataclass(EnvConfig)


# --------------------------------------------------------------------------------------


def _get_jsonschema_specs(dpath: Path) -> dict[str, dict[str, Any]]:
    specs: dict[str, dict[str, Any]] = {}
    for fpath in dpath.iterdir():
        with open(fpath) as f:
            specs[fpath.stem] = json.load(f)  # validates keys
        LOGGER.info(f"validating JSON-schema spec for {fpath}")
        jsonschema.protocols.Validator.check_schema(specs[fpath.stem])
    return specs


# keyed by the mongo collection name
MONGO_COLLECTION_JSONSCHEMA_SPECS = _get_jsonschema_specs(DB_JSONSCHEMA_DIR)


# --------------------------------------------------------------------------------------


def _get_openapi_spec(fpath: Path) -> openapi_core.OpenAPI:
    spec_dict, base_uri = read_from_filename(str(fpath))
    LOGGER.info(f"validating OpenAPI spec for {base_uri} ({fpath})")
    validate(spec_dict)  # no exception -> spec is valid
    return openapi_core.OpenAPI(SchemaPath.from_file_path(str(fpath)))


REST_OPENAPI_SPEC: openapi_core.OpenAPI = _get_openapi_spec(REST_OPENAPI_SPEC_FPATH)
URL_V_PREFIX = (  # ex: v0
    "v" + REST_OPENAPI_SPEC.spec.contents()["info"]["version"].split(".", maxsplit=1)[0]
)


# --------------------------------------------------------------------------------------


# known cluster locations
KNOWN_CLUSTERS: dict[str, dict[str, str]] = {
    "sub-2": {
        "collector": "glidein-cm.icecube.wisc.edu",
        "schedd": "sub-2.icecube.wisc.edu",
    },
}
if ENV.CI:  # just for testing -- can remove when we have 2+ clusters
    KNOWN_CLUSTERS.update(
        {
            "test-alpha": {
                "collector": "COLLECTOR1",
                "schedd": "SCHEDD1",
            },
            "test-beta": {
                "collector": "COLLECTOR2",
                "schedd": "SCHEDD2",
            },
        }
    )


# --------------------------------------------------------------------------------------

GH_API_PILOT_URL = (
    "https://api.github.com/repos/Observation-Management-Service/ewms-pilot"
)

# these are from Taskforce.json
_PILOT_VERSION_PATTERN = re.compile(r"^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$")
_PILOT_BRANCH_FEATURE_PATTERN = re.compile(r"^[a-z0-9._-]+-[a-z0-9]{1,128}$")


@aiocache.cached(ttl=1 * 60)  # don't cache too long, but avoid spamming
async def get_pilot_tag(tag: str) -> str:
    """Get/validate the tag of the pilot image."""
    rc = RestClient(GH_API_PILOT_URL)

    if tag == "latest":  # convert to immutable version tag
        LOGGER.info(f"Retrieving pilot image info ({tag})...")
        try:
            resp = await rc.request("GET", "/releases/latest")
            tag = resp["tag_name"].lstrip("v")
            LOGGER.info(f"latest pilot tag is {tag}")
            return tag
        except Exception as e:
            LOGGER.exception(e)

    elif _PILOT_VERSION_PATTERN.match(tag):  # confirm it exists by name
        LOGGER.info(f"Retrieving pilot image info ({tag})...")
        try:
            resp = await rc.request("GET", "/releases")  # -> list
            if f"v{tag}" in (a["tag_name"] for a in resp):
                # in releases, the tags have a preceding "v"
                LOGGER.debug(f"found pilot image tag {tag}")
                return tag
        except Exception as e:
            LOGGER.exception(e)

    elif _PILOT_BRANCH_FEATURE_PATTERN.match(tag):  # confirm it exists by sha
        # NOW, we're going to assume that the image tag is a "branch tag",
        #    so, grab the commit sha from it and see if that exists.
        #    Ex: apptainer-debug-68594b0 -> 68594b0
        commit_sha = tag.split("-")[-1]
        LOGGER.info(f"Retrieving pilot image info ({tag})...")
        try:
            await rc.request("GET", f"/commits/{commit_sha}")
            LOGGER.debug(f"found pilot image tag (feature branch) {tag}")
            return tag
        except Exception as e:
            LOGGER.exception(e)

    # fall through
    msg = (
        "Pilot image tag not found. "
        "It is possible that the image has not finished uploading to its registry. "
        "If this error persists, contact an EWMS admin."
    )
    raise web.HTTPError(
        status_code=400,
        log_message=msg,
        reason=msg,  # to client
    )


# --------------------------------------------------------------------------------------


def config_logging() -> None:
    """Configure the logging level and format.

    This is separated into a function for consistency between app and
    testing environments.
    """
    hand = logging.StreamHandler()
    hand.setFormatter(
        logging.Formatter(
            "%(asctime)s.%(msecs)03d [%(levelname)8s] %(name)s[%(process)d] %(message)s <%(filename)s:%(lineno)s/%(funcName)s()>",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logging.getLogger().addHandler(hand)

    if not ENV.CI and ENV.LOG_LEVEL.upper() == "DEBUG":
        demoted_first_parties = {
            "wms.taskforce_launch_control": "INFO",
            "wms.workflow_mq_activator": "INFO",
        }
    else:
        demoted_first_parties = {}

    logging_tools.set_level(
        ENV.LOG_LEVEL,  # type: ignore[arg-type]
        first_party_loggers=[__name__.split(".", maxsplit=1)[0]],
        third_party_level=ENV.LOG_LEVEL_THIRD_PARTY,  # type: ignore[arg-type]
        future_third_parties=[],
        specialty_loggers={
            "wipac-telemetry": "WARNING",
            "parse": "WARNING",  # from openapi
            "rest_tools": ENV.LOG_LEVEL_REST_TOOLS,  # type: ignore
            **demoted_first_parties,  # type: ignore
        },
    )
