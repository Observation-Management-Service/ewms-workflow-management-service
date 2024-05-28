# Documentation for EWMS - Workflow Management Service

<a name="documentation-for-api-endpoints"></a>
## Documentation for API Endpoints


| Class | Method | HTTP request | Description |
|------------ | ------------- | ------------- | -------------|
| *DefaultApi* | [**queryTaskDirectivesPost**](Apis/DefaultApi.md#querytaskdirectivespost) | **POST** /query/task-directives |  |
*DefaultApi* | [**queryTaskforcesPost**](Apis/DefaultApi.md#querytaskforcespost) | **POST** /query/taskforces |  |
*DefaultApi* | [**queryWorkflowsPost**](Apis/DefaultApi.md#queryworkflowspost) | **POST** /query/workflows |  |
*DefaultApi* | [**rootGet**](Apis/DefaultApi.md#rootget) | **GET** / |  |
*DefaultApi* | [**schemaOpenapiGet**](Apis/DefaultApi.md#schemaopenapiget) | **GET** /schema/openapi |  |
*DefaultApi* | [**taskDirectivesTaskIdGet**](Apis/DefaultApi.md#taskdirectivestaskidget) | **GET** /task-directives/{task_id} |  |
*DefaultApi* | [**taskforcesTaskforceUuidGet**](Apis/DefaultApi.md#taskforcestaskforceuuidget) | **GET** /taskforces/{taskforce_uuid} |  |
*DefaultApi* | [**tmsCondorCompleteTaskforcesTaskforceUuidPost**](Apis/DefaultApi.md#tmscondorcompletetaskforcestaskforceuuidpost) | **POST** /tms/condor-complete/taskforces/{taskforce_uuid} |  |
*DefaultApi* | [**tmsCondorSubmitTaskforcesTaskforceUuidPost**](Apis/DefaultApi.md#tmscondorsubmittaskforcestaskforceuuidpost) | **POST** /tms/condor-submit/taskforces/{taskforce_uuid} |  |
*DefaultApi* | [**tmsPendingStarterTaskforcesGet**](Apis/DefaultApi.md#tmspendingstartertaskforcesget) | **GET** /tms/pending-starter/taskforces |  |
*DefaultApi* | [**tmsPendingStopperTaskforcesGet**](Apis/DefaultApi.md#tmspendingstoppertaskforcesget) | **GET** /tms/pending-stopper/taskforces |  |
*DefaultApi* | [**tmsPendingStopperTaskforcesTaskforceUuidDelete**](Apis/DefaultApi.md#tmspendingstoppertaskforcestaskforceuuiddelete) | **DELETE** /tms/pending-stopper/taskforces/{taskforce_uuid} |  |
*DefaultApi* | [**tmsStatusesTaskforcesPost**](Apis/DefaultApi.md#tmsstatusestaskforcespost) | **POST** /tms/statuses/taskforces |  |
*DefaultApi* | [**workflowsPost**](Apis/DefaultApi.md#workflowspost) | **POST** /workflows |  |
*DefaultApi* | [**workflowsWorkflowIdDelete**](Apis/DefaultApi.md#workflowsworkflowiddelete) | **DELETE** /workflows/{workflow_id} |  |
*DefaultApi* | [**workflowsWorkflowIdGet**](Apis/DefaultApi.md#workflowsworkflowidget) | **GET** /workflows/{workflow_id} |  |


<a name="documentation-for-models"></a>
## Documentation for Models

 - [FindObject](./Models/FindObject.md)
 - [TaskDirectiveObject](./Models/TaskDirectiveObject.md)
 - [TaskforceObject](./Models/TaskforceObject.md)
 - [TaskforceObject_container_config](./Models/TaskforceObject_container_config.md)
 - [TaskforceObject_container_config_environment_value](./Models/TaskforceObject_container_config_environment_value.md)
 - [TaskforceObject_n_workers](./Models/TaskforceObject_n_workers.md)
 - [TaskforceObject_worker_config](./Models/TaskforceObject_worker_config.md)
 - [TaskforceUUIDObject](./Models/TaskforceUUIDObject.md)
 - [WorkflowObject](./Models/WorkflowObject.md)
 - [__get_400_response](./Models/__get_400_response.md)
 - [_query_task_directives_post_200_response](./Models/_query_task_directives_post_200_response.md)
 - [_query_task_directives_post_400_response](./Models/_query_task_directives_post_400_response.md)
 - [_query_taskforces_post_200_response](./Models/_query_taskforces_post_200_response.md)
 - [_query_workflows_post_200_response](./Models/_query_workflows_post_200_response.md)
 - [_tms_condor_complete_taskforces__taskforce_uuid__post_request](./Models/_tms_condor_complete_taskforces__taskforce_uuid__post_request.md)
 - [_tms_pending_starter_taskforces_get_200_response](./Models/_tms_pending_starter_taskforces_get_200_response.md)
 - [_tms_statuses_taskforces_post_200_response](./Models/_tms_statuses_taskforces_post_200_response.md)
 - [_tms_statuses_taskforces_post_200_response_results_inner](./Models/_tms_statuses_taskforces_post_200_response_results_inner.md)
 - [_tms_statuses_taskforces_post_207_response](./Models/_tms_statuses_taskforces_post_207_response.md)
 - [_tms_statuses_taskforces_post_207_response_results_inner](./Models/_tms_statuses_taskforces_post_207_response_results_inner.md)
 - [_tms_statuses_taskforces_post_request](./Models/_tms_statuses_taskforces_post_request.md)
 - [_workflows__workflow_id__delete_200_response](./Models/_workflows__workflow_id__delete_200_response.md)
 - [_workflows_post_200_response](./Models/_workflows_post_200_response.md)
 - [_workflows_post_request](./Models/_workflows_post_request.md)
 - [_workflows_post_request_tasks_inner](./Models/_workflows_post_request_tasks_inner.md)
 - [worker_config](./Models/worker_config.md)


<a name="documentation-for-authorization"></a>
## Documentation for Authorization

