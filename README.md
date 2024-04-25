<!--- Top of README Badges (automated) --->
[![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/Observation-Management-Service/ewms-workflow-management-service?include_prereleases)](https://github.com/Observation-Management-Service/ewms-workflow-management-service/) [![Lines of code](https://img.shields.io/tokei/lines/github/Observation-Management-Service/ewms-workflow-management-service)](https://github.com/Observation-Management-Service/ewms-workflow-management-service/) [![GitHub issues](https://img.shields.io/github/issues/Observation-Management-Service/ewms-workflow-management-service)](https://github.com/Observation-Management-Service/ewms-workflow-management-service/issues?q=is%3Aissue+sort%3Aupdated-desc+is%3Aopen) [![GitHub pull requests](https://img.shields.io/github/issues-pr/Observation-Management-Service/ewms-workflow-management-service)](https://github.com/Observation-Management-Service/ewms-workflow-management-service/pulls?q=is%3Apr+sort%3Aupdated-desc+is%3Aopen) 
<!--- End of README Badges (automated) --->
# ewms-workflow-management-service
The external interface for EWMS

## API Documentation
See [Docs/](./Docs)

## Task Startup Flow
1. The user requests a new task
1. WMS requests to the MQS for _n_ queues. the MQS tells WMS "not now" (not enough avail resources)
1. WMS waits (alternatively, requests to MQS for other pending tasks)
1. MQS creates queues, and gives them to WMS
1. WMS marks task/taskforce(s) ready for TMS
1. When ready, TMS initiates condor jobs for task/taskforce(s)
