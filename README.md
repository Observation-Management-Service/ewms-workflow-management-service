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
