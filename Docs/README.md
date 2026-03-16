# Documentation for EWMS - Workflow Management Service

<a name="documentation-for-api-endpoints"></a>
## Documentation for API Endpoints


| Class | Method | HTTP request | Description |
|------------ | ------------- | ------------- | -------------|
| *DefaultApi* | [_details_](Apis/DefaultApi.md#get-v1) | **GET** /v1/ | Returns an empty response. |
*DefaultApi* | [_details_](Apis/DefaultApi.md#post-v1querytask-directives) | **POST** /v1/query/task-directives | Queries and returns a list of task directive objects based on the provided criteria. |
*DefaultApi* | [_details_](Apis/DefaultApi.md#post-v1querytaskforces) | **POST** /v1/query/taskforces | Queries and returns a list of taskforce objects based on the provided criteria. |
*DefaultApi* | [_details_](Apis/DefaultApi.md#post-v1queryworkflows) | **POST** /v1/query/workflows | Queries and returns a list of workflow objects based on the provided criteria. |
*DefaultApi* | [_details_](Apis/DefaultApi.md#get-v1schemaopenapi) | **GET** /v1/schema/openapi | Returns the OpenAPI schema. |
*DefaultApi* | [_details_](Apis/DefaultApi.md#post-v1task-directivestask_idactionsadd-workers) | **POST** /v1/task-directives/{task_id}/actions/add-workers | Creates a new taskforce (and associated workers) for an existing task directive. |
*DefaultApi* | [_details_](Apis/DefaultApi.md#get-v1task-directivestask_id) | **GET** /v1/task-directives/{task_id} | Retrieves the task directive that matches the specified task ID. |
*DefaultApi* | [_details_](Apis/DefaultApi.md#get-v1taskforcestaskforce_uuid) | **GET** /v1/taskforces/{taskforce_uuid} | Retrieves the taskforce object that matches the specified taskforce UUID. |
*DefaultApi* | [_details_](Apis/DefaultApi.md#post-v1tmscondor-completetaskforcestaskforce_uuid) | **POST** /v1/tms/condor-complete/taskforces/{taskforce_uuid} | For internal use only (TMS): Updates the specified taskforce with the completion timestamp of the HTCondor cluster. |
*DefaultApi* | [_details_](Apis/DefaultApi.md#post-v1tmscondor-rmtaskforcestaskforce_uuidfailed) | **POST** /v1/tms/condor-rm/taskforces/{taskforce_uuid}/failed | For internal use only (TMS): Communicates that a taskforce failed to be removed on HTCondor. |
*DefaultApi* | [_details_](Apis/DefaultApi.md#post-v1tmscondor-rmtaskforcestaskforce_uuid) | **POST** /v1/tms/condor-rm/taskforces/{taskforce_uuid} | For internal use only (TMS): Confirms that a taskforce has been removed on HTCondor. |
*DefaultApi* | [_details_](Apis/DefaultApi.md#post-v1tmscondor-submittaskforcestaskforce_uuidfailed) | **POST** /v1/tms/condor-submit/taskforces/{taskforce_uuid}/failed | For internal use only (TMS): Communicates that a taskforce failed to be submitted to HTCondor for execution. |
*DefaultApi* | [_details_](Apis/DefaultApi.md#post-v1tmscondor-submittaskforcestaskforce_uuid) | **POST** /v1/tms/condor-submit/taskforces/{taskforce_uuid} | For internal use only (TMS): Confirms that a taskforce has been submitted to HTCondor for execution. |
*DefaultApi* | [_details_](Apis/DefaultApi.md#get-v1tmspending-startertaskforces) | **GET** /v1/tms/pending-starter/taskforces | For internal use only (TMS): Retrieves the next taskforce ready to start at the specified HTCondor location. |
*DefaultApi* | [_details_](Apis/DefaultApi.md#get-v1tmspending-stoppertaskforces) | **GET** /v1/tms/pending-stopper/taskforces | For internal use only (TMS): Retrieves the next taskforce ready to stop at the specified HTCondor location. |
*DefaultApi* | [_details_](Apis/DefaultApi.md#post-v1tmsstatusestaskforces) | **POST** /v1/tms/statuses/taskforces | For internal use only (TMS): Updates and returns the statuses and errors for the specified taskforces. |
*DefaultApi* | [_details_](Apis/DefaultApi.md#post-v1workflows) | **POST** /v1/workflows | Creates a new workflow along with its associated task directives and taskforces. |
*DefaultApi* | [_details_](Apis/DefaultApi.md#post-v1workflowsworkflow_idactionsabort) | **POST** /v1/workflows/{workflow_id}/actions/abort | Aborts the specified workflow (and marks as 'deactivated'), then sends stop commands to the associated taskforces. |
*DefaultApi* | [_details_](Apis/DefaultApi.md#post-v1workflowsworkflow_idactionsfinished) | **POST** /v1/workflows/{workflow_id}/actions/finished | Marks the specified workflow as finished (and 'deactivated'), then sends stop commands to the associated taskforces. |
*DefaultApi* | [_details_](Apis/DefaultApi.md#get-v1workflowsworkflow_id) | **GET** /v1/workflows/{workflow_id} | Retrieves the workflow object that matches the specified workflow ID. |


<a name="documentation-for-models"></a>
## Documentation for Models

 - [DeactivatedWorkflowResponseObject](./Models/DeactivatedWorkflowResponseObject.md)
 - [FindObject](./Models/FindObject.md)
 - [TaskDirectiveObject](./Models/TaskDirectiveObject.md)
 - [TaskforceObject](./Models/TaskforceObject.md)
 - [TaskforceObject_pilot_config](./Models/TaskforceObject_pilot_config.md)
 - [TaskforceObject_pilot_config_environment_value](./Models/TaskforceObject_pilot_config_environment_value.md)
 - [TaskforceObject_submit_dict_value](./Models/TaskforceObject_submit_dict_value.md)
 - [TaskforceObject_worker_config](./Models/TaskforceObject_worker_config.md)
 - [TaskforceObject_worker_config_worker_disk](./Models/TaskforceObject_worker_config_worker_disk.md)
 - [TaskforceObject_worker_config_worker_memory](./Models/TaskforceObject_worker_config_worker_memory.md)
 - [WorkflowObject](./Models/WorkflowObject.md)
 - [_v1__get_400_response](./Models/_v1__get_400_response.md)
 - [_v1_query_task_directives_post_200_response](./Models/_v1_query_task_directives_post_200_response.md)
 - [_v1_query_task_directives_post_400_response](./Models/_v1_query_task_directives_post_400_response.md)
 - [_v1_query_taskforces_post_200_response](./Models/_v1_query_taskforces_post_200_response.md)
 - [_v1_query_workflows_post_200_response](./Models/_v1_query_workflows_post_200_response.md)
 - [_v1_task_directives__task_id__actions_add_workers_post_request](./Models/_v1_task_directives__task_id__actions_add_workers_post_request.md)
 - [_v1_tms_condor_complete_taskforces__taskforce_uuid__post_200_response](./Models/_v1_tms_condor_complete_taskforces__taskforce_uuid__post_200_response.md)
 - [_v1_tms_condor_complete_taskforces__taskforce_uuid__post_request](./Models/_v1_tms_condor_complete_taskforces__taskforce_uuid__post_request.md)
 - [_v1_tms_condor_rm_taskforces__taskforce_uuid__failed_post_request](./Models/_v1_tms_condor_rm_taskforces__taskforce_uuid__failed_post_request.md)
 - [_v1_tms_condor_submit_taskforces__taskforce_uuid__failed_post_request](./Models/_v1_tms_condor_submit_taskforces__taskforce_uuid__failed_post_request.md)
 - [_v1_tms_pending_starter_taskforces_get_200_response](./Models/_v1_tms_pending_starter_taskforces_get_200_response.md)
 - [_v1_tms_pending_starter_taskforces_get_200_response_anyOf](./Models/_v1_tms_pending_starter_taskforces_get_200_response_anyOf.md)
 - [_v1_tms_pending_stopper_taskforces_get_200_response](./Models/_v1_tms_pending_stopper_taskforces_get_200_response.md)
 - [_v1_tms_statuses_taskforces_post_200_response](./Models/_v1_tms_statuses_taskforces_post_200_response.md)
 - [_v1_tms_statuses_taskforces_post_200_response_results_inner](./Models/_v1_tms_statuses_taskforces_post_200_response_results_inner.md)
 - [_v1_tms_statuses_taskforces_post_207_response](./Models/_v1_tms_statuses_taskforces_post_207_response.md)
 - [_v1_tms_statuses_taskforces_post_207_response_results_inner](./Models/_v1_tms_statuses_taskforces_post_207_response_results_inner.md)
 - [_v1_tms_statuses_taskforces_post_request](./Models/_v1_tms_statuses_taskforces_post_request.md)
 - [_v1_workflows_post_200_response](./Models/_v1_workflows_post_200_response.md)
 - [_v1_workflows_post_request](./Models/_v1_workflows_post_request.md)
 - [_v1_workflows_post_request_tasks_inner](./Models/_v1_workflows_post_request_tasks_inner.md)
 - [pilot_config](./Models/pilot_config.md)
 - [worker_config](./Models/worker_config.md)


<a name="documentation-for-authorization"></a>
## Documentation for Authorization

