"""Config settings."""


import dataclasses as dc
import logging
from typing import Any

from wipac_dev_tools import from_environment_as_dataclass, logging_tools

# --------------------------------------------------------------------------------------
# Constants


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


# known cluster locations
KNOWN_CLUSTERS: dict[str, dict[str, Any]] = {
    "sub-2": {
        "location": {
            "collector": "glidein-cm.icecube.wisc.edu",
            "schedd": "sub-2.icecube.wisc.edu",
        },
    },
}


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
