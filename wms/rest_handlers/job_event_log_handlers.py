"""REST handlers for condor job event log-related routes."""


import logging

LOGGER = logging.getLogger(__name__)


f"/tms/job-event-log/{urllib.parse.quote(str(jel_fpath),safe='')}",
