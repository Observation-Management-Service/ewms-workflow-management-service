"""Config settings."""


import dataclasses as dc
import json
import logging
from pathlib import Path
from typing import Any

import jsonschema
import referencing
from openapi_core import OpenAPI  # type: ignore[attr-defined]
from openapi_spec_validator import validate
from openapi_spec_validator.readers import read_from_filename
from wipac_dev_tools import from_environment_as_dataclass, logging_tools

LOGGER = logging.getLogger(__name__)


# --------------------------------------------------------------------------------------


def _get_json_schema_specs(fpath: Path) -> dict[str, jsonschema.protocols.Validator]:
    with open(fpath) as f:
        dicto = json.load(f)
    for key, entry in dicto.items():
        LOGGER.info(f"validating JSON-schema spec for {key} ({fpath})")
        jsonschema.protocols.Validator.check_schema(entry)
    return {k: jsonschema.protocols.Validator(v) for k, v in dicto.items()}


DATABASE_JSON_SCHEMA_LOOKUP = _get_json_schema_specs(
    Path(__file__).parent / "schema/database_schema.json"
)


# --------------------------------------------------------------------------------------


def _get_openapi_spec(fpath: Path) -> OpenAPI:
    spec_dict, base_uri = read_from_filename(str(fpath))
    LOGGER.info(f"validating OpenAPI spec for {base_uri} ({fpath})")
    validate(spec_dict)  # no exception -> spec is valid
    return OpenAPI.from_file_path(fpath)


REST_OPENAPI_SPEC = _get_openapi_spec(
    Path(__file__).parent / "schema/rest_openapi.json"
)


# --------------------------------------------------------------------------------------


@dc.dataclass(frozen=True)
class EnvConfig:
    """Environment variables."""

    # pylint:disable=invalid-name
    AUTH_AUDIENCE: str = "skydriver"
    AUTH_OPENID_URL: str = ""
    MONGODB_AUTH_PASS: str = ""  # empty means no authentication required
    MONGODB_AUTH_USER: str = ""  # None means required to specify
    MONGODB_HOST: str = "localhost"
    MONGODB_PORT: int = 27017
    REST_HOST: str = "localhost"
    REST_PORT: int = 8080
    CI_TEST: bool = False
    LOG_LEVEL: str = "DEBUG"
    LOG_LEVEL_THIRD_PARTY: str = "WARNING"

    BACKLOG_MIN_PRIORITY_TO_START_NOW: int = 10
    BACKLOG_MAX_ATTEMPTS: int = 3
    BACKLOG_RUNNER_SHORT_DELAY: int = 15
    BACKLOG_RUNNER_DELAY: int = 5 * 60
    BACKLOG_PENDING_ENTRY_TTL_REVIVE: int = 5 * 60  # entry is revived after N secs


ENV = from_environment_as_dataclass(EnvConfig)


# --------------------------------------------------------------------------------------


# known cluster locations
KNOWN_CLUSTERS: dict[str, dict[str, Any]] = {
    "sub-2": {
        "location": {
            "collector": "glidein-cm.icecube.wisc.edu",
            "schedd": "sub-2.icecube.wisc.edu",
        },
    },
}


# --------------------------------------------------------------------------------------


def is_testing() -> bool:
    """Return true if this is the test environment.

    Note: this needs to run on import.
    """
    return ENV.CI_TEST


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
    logging_tools.set_level(
        ENV.LOG_LEVEL,  # type: ignore[arg-type]
        first_party_loggers=__name__.split(".", maxsplit=1)[0],
        third_party_level=ENV.LOG_LEVEL_THIRD_PARTY,  # type: ignore[arg-type]
        future_third_parties=[],
    )
