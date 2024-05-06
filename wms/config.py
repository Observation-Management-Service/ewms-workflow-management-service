"""Config settings."""

import dataclasses as dc
import json
import logging
from pathlib import Path
from typing import Any

import jsonschema
import openapi_core
from jsonschema_path import SchemaPath
from openapi_spec_validator import validate
from openapi_spec_validator.readers import read_from_filename
from wipac_dev_tools import from_environment_as_dataclass, logging_tools

LOGGER = logging.getLogger(__name__)

DB_JSONSCHEMA_DIR = Path(__file__).parent / "schema/db"
REST_OPENAPI_SPEC_FPATH = Path(__file__).parent / "schema/rest/openapi_compiled.json"

MQS_NOT_NOW_HTTP_CODE = 1
MQS_RETRY_AT_TS_DEFAULT_VALUE = float("inf")


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

    TASK_MQ_ASSEMBLY_DELAY: int = 15
    TASK_MQ_ASSEMBLY_MQS_RETRY_WAIT: int = 60
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
            "wms.task_mq_assembly": "INFO",
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
