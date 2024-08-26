<!--- Top of README Badges (automated) --->
[![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/Observation-Management-Service/ewms-workflow-management-service?include_prereleases)](https://github.com/Observation-Management-Service/ewms-workflow-management-service/) [![Lines of code](https://img.shields.io/tokei/lines/github/Observation-Management-Service/ewms-workflow-management-service)](https://github.com/Observation-Management-Service/ewms-workflow-management-service/) [![GitHub issues](https://img.shields.io/github/issues/Observation-Management-Service/ewms-workflow-management-service)](https://github.com/Observation-Management-Service/ewms-workflow-management-service/issues?q=is%3Aissue+sort%3Aupdated-desc+is%3Aopen) [![GitHub pull requests](https://img.shields.io/github/issues-pr/Observation-Management-Service/ewms-workflow-management-service)](https://github.com/Observation-Management-Service/ewms-workflow-management-service/pulls?q=is%3Apr+sort%3Aupdated-desc+is%3Aopen)
<!--- End of README Badges (automated) --->

# ewms-workflow-management-service

The external interface for EWMS

## API Documentation

See [Docs/](./Docs)

## EWMS Workflow Startup Overview

1. The user requests a new workflow (**POST
   ** [/v0/workflows](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/main/Docs/Apis/DefaultApi.md#v0WorkflowsPost))
1. WMS requests to the MQS for _n_ queues
    1. _if the MQS tells WMS "not now"_ (not sufficient available resources), then WMS waits (in the meantime, WMS
       requests to MQS for other pending workflows)
    2. else/eventually, MQS creates queues and gives them to WMS
1. WMS marks workflow's taskforce(s) ready for TMS
1. When ready, TMS initiates HTCondor jobs for taskforce(s)

## EWMS Glossary Applied to the WMS

### Workflow

The **workflow**, in the hierarchy of EWMS objects, is the highest-level object, it comprises 1+ **tasks** (each described by a **task directive**). These tasks are related by their **message queues**, like edges and nodes in a graph. [More docs.](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/main/Docs/Models/WorkflowObject.md)

### Message Queue

The **message queue** is used to transfer data to and/or from a task. Publicly-accessible message queues can be used to inject and/or dump data from/to an external location. This flexibility allows creating **workflows** of a wide range of complexity: think graph theory. A message queue is identified by an ID and requires an authentication token to access.

### Task

Throughout EWMS, the term, **task**, is context dependant. At the highest level (in the user context), this is the thing we want to parallelize. At the lowest level (in the context of the EWMS [pilot](https://github.com/Observation-Management-Service/ewms-pilot)), a task is a runtime instance of the task container triggered by an inbound **event** received from a **message queue**.

Somewhere in the middle (the WMS context), a **task** is the unique combination of an image, arguments, environment variables, etc. Because of this ambiguity, the **task directive** serves as a first-order object within the WMS.

### Task Directive

The **task directive** is the first-order object that represents the unique configuration of a task and its position within an EWMS **workflow**. This object is immutable. Note: the primary key of this object is `task_id`. [More docs.](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/main/Docs/Models/TaskDirectiveObject.md)

### Taskforce

Unlike most of the objects above, a **taskforce** is not explicitly created by a user. It exists as a two-way bridge between the EWMS-world and the HTCondor-world. A **taskforce** is created for each application of a **task directive**, an N:1 mapping. It contains HTCondor compute instructions and runtime status information. A taskforce is applied to 1 HTCondor cluster and so, has a fixed number of workers. If increased compute is needed (i.e. more workers), additional taskforces are created from the same **task directive**. [More docs.](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/main/Docs/Models/TaskforceObject.md)
