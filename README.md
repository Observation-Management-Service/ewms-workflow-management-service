<!--- Top of README Badges (automated) --->
[![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/Observation-Management-Service/ewms-workflow-management-service?include_prereleases)](https://github.com/Observation-Management-Service/ewms-workflow-management-service/) [![Lines of code](https://img.shields.io/tokei/lines/github/Observation-Management-Service/ewms-workflow-management-service)](https://github.com/Observation-Management-Service/ewms-workflow-management-service/) [![GitHub issues](https://img.shields.io/github/issues/Observation-Management-Service/ewms-workflow-management-service)](https://github.com/Observation-Management-Service/ewms-workflow-management-service/issues?q=is%3Aissue+sort%3Aupdated-desc+is%3Aopen) [![GitHub pull requests](https://img.shields.io/github/issues-pr/Observation-Management-Service/ewms-workflow-management-service)](https://github.com/Observation-Management-Service/ewms-workflow-management-service/pulls?q=is%3Apr+sort%3Aupdated-desc+is%3Aopen)
<!--- End of README Badges (automated) --->

# ewms-workflow-management-service

A Workflow Management Service for EWMS

The WMS is both the central component and the external interface for the Event Workflow Management System (EWMS). This service:

- **Processes requests** for HTCondor-served, [task](#task)-based [workflows](#workflow).
- **Translates workflows** into actionable instructions.
- **Coordinates assignments** among EWMS components.
- **Manages workloads** based on available resources and workflow status.
- **Relays** information (workflow statuses, history, etc.) to external parties on demand.

## API Documentation

See [Docs/](./Docs)

## Overview

As described [above](#ewms-workflow-management-service), the WMS has several concurrent responsibilities. These actions can be outlined in the "story" of a workflow:

### EWMS Workflow Lifetime

1. The user requests a new [workflow](#workflow). The WMS translates this workflow into _n_ [task directives](#task-directive), _m_ [taskforces](#taskforce), and determines the number of required queues.
    - [POST @ /v0/workflows](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/main/Docs/Apis/DefaultApi.md#v0WorkflowsPost)
2. The WMS requests _p_ queues from the [MQS](https://github.com/Observation-Management-Service/ewms-message-queue-service):
    1. If the MQS indicates that resources are insufficient, the WMS waits and also requests any other pending workflows from the MQS.
    2. Otherwise/eventually, the MQS creates the queues and provides them to the WMS.
3. The WMS makes tokens for any publicly accessible queues available to the user.
    - [GET @ /v0/mqs/workflows/{workflow_id}/mq-profiles/public](https://github.com/Observation-Management-Service/ewms-message-queue-service/blob/main/Docs/Apis/DefaultApi.md#v0MqsWorkflowsWorkflowIdMqProfilesPublicGet)
4. The WMS marks the workflow's taskforce(s) as ready for the [TMS](https://github.com/Observation-Management-Service/ewms-task-management-service).
    - See [taskforce.phase](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/main/Docs/Models/TaskforceObject.md)
5. When ready, the TMS initiates HTCondor jobs for the taskforce(s).
6. The TMS relays live, aggregated runtime statuses to the WMS until the workflow's taskforces are completed.
    - See [taskforce.compound_statuses](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/main/Docs/Models/TaskforceObject.md) and/or [taskforce.top_task_errors](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/main/Docs/Models/TaskforceObject.md)

This "story" is also detailed in [request_workflow.py](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/readme/examples/request_workflow.py). However, this script may not suit your needs well. It is recommended to have a solid understanding of the user-facing [endpoints and objects](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/readme/Docs/README.md).

### First-Order Object Endpoints

Understanding the [objects](#ewms-glossary-applied-to-the-wms) within the WMS (and EWMS) is key. The following REST endpoints allow users to retrieve these objects.

#### Get a Workflow

_What's a [workflow](#workflow)?_

- Get by ID: [GET @ /v0/workflows/{workflow_id}](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/main/Docs/Apis/DefaultApi.md#v0workflowsworkflowidget)
- Search by other criteria: [POST /v0/query/workflows](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/main/Docs/Apis/DefaultApi.md#v0queryworkflowspost)

#### Get a Task Directive

_What's a [task directive](#task-directive)?_

- Get by ID: [GET @ /v0/task-directives/{task_id}](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/main/Docs/Apis/DefaultApi.md#v0taskdirectivestaskidget)
- Search by other criteria: [POST @ /v0/query/task-directives](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/main/Docs/Apis/DefaultApi.md#v0querytaskdirectivespost)

#### Get a Taskforce

_What's a [taskforce](#taskforce)?_

- Get by ID: [GET @ /v0/taskforces/{taskforce_uuid}](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/main/Docs/Apis/DefaultApi.md#v0taskforcestaskforceuuidget)
- Search by other criteria: [POST @ /v0/query/taskforces](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/main/Docs/Apis/DefaultApi.md#v0querytaskforcespost)

## EWMS Glossary Applied to the WMS

### Workflow

The **workflow** is the highest-level object in the EWMS hierarchy. It consists of 1+ **tasks**, each described by a **task directive**. These tasks are connected by **message queues**, similar to nodes and edges in a graph.  
[More documentation](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/main/Docs/Models/WorkflowObject.md).

### Message Queue

The **message queue** transfers **events** to and from a task. Public message queues allow external event injection or retrieval. This flexibility supports creating **workflows** of various complexity, similar to graph theory. Each message queue is identified by an ID and requires an authentication token for access.

#### Event

An **event** is an object transferred via **message queues**. It is the most frequently occurring object in EWMS. See [above](#message-queue).

### Task

The term **task** has different meanings depending on the context within EWMS:

- **User context**: A task is a unit of work intended for parallelization.
- **EWMS pilot context**: A task is a runtime instance of the task container (similar to a mathematical function), applied to an inbound **event** from a **message queue** and potentially produces outbound events.
- **WMS context**: A **task** refers to the unique combination of a workflow instance, image, arguments, environment variables, etc.

Due to this ambiguity, the **task directive** is considered a first-order object within the WMS.

### Task Directive

The **task directive** represents the unique configuration of a task and its place within an EWMS **workflow**. This object is immutable, with `task_id` as its primary key.  
[More documentation](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/main/Docs/Models/TaskDirectiveObject.md).

### Taskforce

A **taskforce** is not explicitly created by the user. It serves as a two-way bridge between EWMS and HTCondor. A **taskforce** is created for each application of a **task directive** (N:1 mapping) and contains HTCondor compute instructions and runtime status information. Each taskforce is applied to a single HTCondor cluster, with a fixed number of workers. If more compute resources are needed, additional taskforces are created from the same **task directive**.  
[More documentation](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/main/Docs/Models/TaskforceObject.md).
