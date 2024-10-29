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
- **Relays information** (workflow statuses, history, etc.) to external parties on demand.

## API Documentation

See [Docs/](./Docs)

## Overview

As described [above](#ewms-workflow-management-service), the WMS has several concurrent responsibilities. These actions can be outlined in the "story" of a workflow:

### EWMS Workflow Lifetime

1. The user requests a new [workflow](#workflow). The WMS translates this workflow into _n_ [task directives](#task-directive), _m_ [taskforces](#taskforce), and determines the number of required queues.
    - [POST @ /v0/workflows](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/main/Docs/Apis/DefaultApi.md#post-v0workflows)
    - See [Example Workflow Request JSON](#example-workflow-request-json)
2. The WMS requests _p_ queues from the [MQS](https://github.com/Observation-Management-Service/ewms-message-queue-service):
    1. If the MQS indicates that resources are insufficient, the WMS waits and also requests any other pending workflows from the MQS.
    2. Otherwise/eventually, the MQS creates the queues and provides them to the WMS.
3. The WMS makes tokens for any publicly accessible queues available to the user.
    - [GET @ /v0/mqs/workflows/{workflow_id}/mq-profiles/public](https://github.com/Observation-Management-Service/ewms-message-queue-service/blob/main/Docs/Apis/DefaultApi.md#v0MqsWorkflowsWorkflowIdMqProfilesPublicGet)
4. The WMS marks the workflow's taskforce(s) as ready for the [TMS](https://github.com/Observation-Management-Service/ewms-task-management-service).
    - See [`Taskforce.phase`](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/main/Docs/Models/TaskforceObject.md)
5. When ready, the TMS initiates HTCondor jobs for the taskforce(s).
6. The TMS relays live, aggregated runtime statuses to the WMS until the workflow's taskforces are completed.
    - See [`Taskforce.compound_statuses`](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/main/Docs/Models/TaskforceObject.md) and/or [`Taskforce.top_task_errors`](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/main/Docs/Models/TaskforceObject.md)
7. The user tells EWMS that the workflow has finished. The workflow is deactivated, and the TMS stops the associated taskforces.
    - [POST @ /v0/workflows/{workflow_id}/actions/finished](https://github.com/Observation-Management-Service/ewms-message-queue-service/blob/main/Docs/Apis/DefaultApi.md#post-v0workflowsworkflow_idactionsfinished)

This "story" is also detailed in [request_workflow.py](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/readme/examples/request_workflow.py). However, this script may not suit all your needs. It is recommended to have a solid understanding of the user-facing [API endpoints](https://github.com/Observation-Management-Service/ewms-workflow-management-service/tree/main/Docs#documentation-for-api-endpoints) and [objects](https://github.com/Observation-Management-Service/ewms-workflow-management-service/tree/main/Docs#documentation-for-models).

#### Example Workflow Request JSON

Every [workflow](#workflow)) originates from a JSON object using [POST @ /v0/workflows](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/main/Docs/Apis/DefaultApi.md#post-v0workflows). The following is an example of valid a request object (refer to the [docs](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/main/Docs/Models/_v0_workflows_post_request.md) for other optional fields not seen here):

```json
{
    "public_queue_aliases": [
        "input-queue",
        "output-queue"
    ],
    "tasks": [
        {
            "cluster_locations": [
                "sub-2"
            ],
            "input_queue_aliases": [
                "input-queue"
            ],
            "output_queue_aliases": [
                "output-queue"
            ],
            "task_image": "/cvmfs/icecube.opensciencegrid.org/containers/path/to/my-apptainer-container:1.2.3",
            "task_args": "cp {{INFILE}} {{OUTFILE}}",
            "n_workers": 1000,
            "worker_config": {
                "do_transfer_worker_stdouterr": true,
                "max_worker_runtime": 600,
                "n_cores": 1,
                "priority": 99,
                "worker_disk": "512M",
                "worker_memory": "512M"
            }
        }
    ]
}
```

#### The Task Container

The task container is built from the user-provided image, specified by the [workflow request object's `task_image`, `task_args`, and `task_env`](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/main/Docs/Apis/DefaultApi.md#post-v0workflows). The container runs within an [EWMS Pilot instance](https://github.com/Observation-Management-Service/ewms-pilot) on an HTCondor Execution Point (EP). For configuration and interaction with EWMS [events](#event), refer to the [EWMS Pilot documentation](https://github.com/Observation-Management-Service/ewms-pilot).

##### The Init Container

The init container runs once on a worker before any task/event is processed. This is specified by the [workflow request object's `init_image`, `init_args`, and `init_env`](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/main/Docs/Apis/DefaultApi.md#post-v0workflows). See the [EWMS Pilot documentation](https://github.com/Observation-Management-Service/ewms-pilot#the-init-container) for more information.

##### Locations of Persisted Attributes

The [workflow request object's](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/main/Docs/Apis/DefaultApi.md#post-v0workflows) fields are mostly persisted in similarly-named fields the [`TaskDirective`](#task-directive) object. However, some are located in other places:

| POST @ `/v0/workflows` Field | Persisted Destination                                                                      |
|------------------------------|--------------------------------------------------------------------------------------------|
| `task_image`                 | `TaskDirective.task_image` and `Taskforce.pilot_config.environment.EWMS_PILOT_TASK_IMAGE`  |
| `task_args`                  | `TaskDirective.task_args` and `Taskforce.pilot_config.environment.EWMS_PILOT_TASK_ARGS`    |
| `task_env`                   | `Taskforce.pilot_config.environment.EWMS_PILOT_TASK_ENV_JSON` (as a JSON-string)           |
| `init_image`                 | `Taskforce.pilot_config.environment.EWMS_PILOT_INIT_IMAGE`                                 |
| `init_args`                  | `Taskforce.pilot_config.environment.EWMS_PILOT_INIT_ARGS`                                  |
| `init_env`                   | `Taskforce.pilot_config.environment.EWMS_PILOT_INIT_ENV_JSON` (as a JSON-string)           |
| `pilot_config`               | `Taskforce.pilot_config` (with additions to the `environment` sub-field, like those above) |
| `worker_config`              | `Taskforce.worker_config`                                                                  |
| `n_workers`                  | `Taskforce.n_workers`                                                                      |

### Interacting with First-Order Objects using API Endpoints

Understanding the [objects](#ewms-glossary-applied-to-the-wms) within the WMS (and EWMS) is key. The following REST endpoints allow users to retrieve with these objects.

#### Get a Workflow

_What's a [workflow](#workflow)?_

- Get by ID: [GET @ /v0/workflows/{workflow_id}](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/main/Docs/Apis/DefaultApi.md#get-v0workflowsworkflow-id)
- Search by other criteria: [POST @ /v0/query/workflows](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/main/Docs/Apis/DefaultApi.md#post-v0workflows)

#### Get a Task Directive

_What's a [task directive](#task-directive)?_

- Get by ID: [GET @ /v0/task-directives/{task_id}](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/main/Docs/Apis/DefaultApi.md#get-v0task-directivestask_id)
- Search by other criteria: [POST @ /v0/query/task-directives](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/main/Docs/Apis/DefaultApi.md#post-v0querytask-directives)

#### Get a Taskforce

_What's a [taskforce](#taskforce)?_

- Get by ID: [GET @ /v0/taskforces/{taskforce_uuid}](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/main/Docs/Apis/DefaultApi.md#get-v0taskforcestaskforce_uuid)
- Search by other criteria: [POST @ /v0/query/taskforces](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/main/Docs/Apis/DefaultApi.md#post-v0querytaskforces)

## EWMS Glossary Applied to the WMS

### Workflow

The **workflow** is the highest-level object in the EWMS hierarchy. It consists of 1+ **tasks**, each described by a **task directive**. These tasks are connected by **message queues**, akin to nodes and edges in a graph. _[See object properties.](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/main/Docs/Models/WorkflowObject.md)_

_How is a [workflow](#get-a-workflow) object retrieved?_

### Message Queue

The **message queue** transfers **events** to and from a task. Public message queues allow external event injection or retrieval. This flexibility supports creating **workflows** of various complexity (graph theory). Each message queue is identified by an ID and requires an authentication token for access.

#### Event

An **event** is an object transferred via **message queues**. It is the most frequently occurring object in EWMS.

### Task

A **task** refers to the unique combination of a workflow instance, container image, runtime arguments, environment variables, etc.

The term **task** also has **different meanings depending on the context** within EWMS:

- **User context**: A task is a unit of work intended for parallelization.
- **[EWMS pilot context](#the-task-container)**: A task is a runtime instance of the task container, applied to an inbound **event** from a **message queue** and potentially produces outbound events (akin to a mathematical function).

_Due to this ambiguity, the [**task directive**](#task-directive) is considered a first-order object within the WMS._

### Task Directive

The **task directive** represents the unique configuration of a [task](#task) (WMS context) and its place within an EWMS **workflow**. This object is immutable, with `task_id` as its primary key. _[See object properties.](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/main/Docs/Models/TaskDirectiveObject.md)_

_How is a [task directive](#get-a-task-directive) object retrieved?_

### Taskforce

A **taskforce** is not explicitly created by the user. It serves as a two-way bridge between EWMS and HTCondor. A **taskforce** is created for each application of a **task directive** (N:1 mapping) and contains HTCondor compute instructions and runtime status information. Each taskforce is applied to a single HTCondor cluster, with a fixed number of workers. If more compute resources are needed, additional taskforces are created from the same **task directive**. _[See object properties.](https://github.com/Observation-Management-Service/ewms-workflow-management-service/blob/main/Docs/Models/TaskforceObject.md)_

_How is a [taskforce](#get-a-taskforce) object retrieved?_
