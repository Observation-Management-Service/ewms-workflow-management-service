"""Config settings."""

import dataclasses as dc
import json
import logging
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import cachetools.func
import jsonschema
import openapi_core
import requests
from jsonschema_path import SchemaPath
from openapi_spec_validator import validate
from openapi_spec_validator.readers import read_from_filename
from tornado import web
from wipac_dev_tools import from_environment_as_dataclass, logging_tools

LOGGER = logging.getLogger(__name__)

DB_JSONSCHEMA_DIR = Path(__file__).parent / "schema/db"
REST_OPENAPI_SPEC_FPATH = Path(__file__).parent / "schema/rest/openapi_compiled.json"

MQS_RETRY_AT_TS_DEFAULT_VALUE = float("inf")
TASK_MQ_ACTIVATOR_SHORTEST_SLEEP = 1


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

    WORKFLOW_MQ_ACTIVATOR_DELAY: int = 15
    WORKFLOW_MQ_ACTIVATOR_MQS_RETRY_WAIT: int = 60
    TASKFORCE_LAUNCH_CONTROL_DELAY: int = 1


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
ROUTE_VERSION_PREFIX = (  # ex: v0
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


GH_API_PILOT_RELEASES_URL = (  # can't end in '/'
    "https://api.github.com/repos/Observation-Management-Service/ewms-pilot/releases"
)


@cachetools.func.ttl_cache(ttl=1 * 60)
def get_pilot_image(tag: str) -> str:
    """Get the uri to the pilot image."""
    if tag == "latest":  # convert to immutable version tag
        url = urljoin(GH_API_PILOT_RELEASES_URL + "/", "latest")
        LOGGER.info(f"Retrieving pilot image info from {url} ...")
        resp = requests.get(url)
        LOGGER.debug(resp)
        tag = resp.json()["tag_name"]
    else:
        LOGGER.info(f"Retrieving pilot image info from {GH_API_PILOT_RELEASES_URL} ...")
        all_em = [a["tag_name"] for a in requests.get(GH_API_PILOT_RELEASES_URL).json()]
        LOGGER.debug(all_em)
        if tag not in all_em:
            msg = f"pilot image not found: {tag}"
            raise web.HTTPError(
                status_code=400,
                log_message=msg,
                reason=msg,  # to client
            )

    return tag


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
