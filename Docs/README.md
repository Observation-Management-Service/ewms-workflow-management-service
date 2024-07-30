# Documentation for EWMS - Workflow Management Service

<a name="documentation-for-api-endpoints"></a>
## Documentation for API Endpoints


| Class | Method | HTTP request | Description |
|------------ | ------------- | ------------- | -------------|
| *DefaultApi* | [**v0Get**](Apis/DefaultApi.md#v0get) | **GET** /v0/ |  |
*DefaultApi* | [**v0QueryTaskDirectivesPost**](Apis/DefaultApi.md#v0querytaskdirectivespost) | **POST** /v0/query/task-directives |  |
*DefaultApi* | [**v0QueryTaskforcesPost**](Apis/DefaultApi.md#v0querytaskforcespost) | **POST** /v0/query/taskforces |  |
*DefaultApi* | [**v0QueryWorkflowsPost**](Apis/DefaultApi.md#v0queryworkflowspost) | **POST** /v0/query/workflows |  |
*DefaultApi* | [**v0SchemaOpenapiGet**](Apis/DefaultApi.md#v0schemaopenapiget) | **GET** /v0/schema/openapi |  |
*DefaultApi* | [**v0TaskDirectivesTaskIdGet**](Apis/DefaultApi.md#v0taskdirectivestaskidget) | **GET** /v0/task-directives/{task_id} |  |
*DefaultApi* | [**v0TaskforcesTaskforceUuidGet**](Apis/DefaultApi.md#v0taskforcestaskforceuuidget) | **GET** /v0/taskforces/{taskforce_uuid} |  |
*DefaultApi* | [**v0TmsCondorCompleteTaskforcesTaskforceUuidPost**](Apis/DefaultApi.md#v0tmscondorcompletetaskforcestaskforceuuidpost) | **POST** /v0/tms/condor-complete/taskforces/{taskforce_uuid} |  |
*DefaultApi* | [**v0TmsCondorSubmitTaskforcesTaskforceUuidPost**](Apis/DefaultApi.md#v0tmscondorsubmittaskforcestaskforceuuidpost) | **POST** /v0/tms/condor-submit/taskforces/{taskforce_uuid} |  |
*DefaultApi* | [**v0TmsPendingStarterTaskforcesGet**](Apis/DefaultApi.md#v0tmspendingstartertaskforcesget) | **GET** /v0/tms/pending-starter/taskforces |  |
*DefaultApi* | [**v0TmsPendingStopperTaskforcesGet**](Apis/DefaultApi.md#v0tmspendingstoppertaskforcesget) | **GET** /v0/tms/pending-stopper/taskforces |  |
*DefaultApi* | [**v0TmsPendingStopperTaskforcesTaskforceUuidDelete**](Apis/DefaultApi.md#v0tmspendingstoppertaskforcestaskforceuuiddelete) | **DELETE** /v0/tms/pending-stopper/taskforces/{taskforce_uuid} |  |
*DefaultApi* | [**v0TmsStatusesTaskforcesPost**](Apis/DefaultApi.md#v0tmsstatusestaskforcespost) | **POST** /v0/tms/statuses/taskforces |  |
*DefaultApi* | [**v0WorkflowsPost**](Apis/DefaultApi.md#v0workflowspost) | **POST** /v0/workflows |  |
*DefaultApi* | [**v0WorkflowsWorkflowIdDelete**](Apis/DefaultApi.md#v0workflowsworkflowiddelete) | **DELETE** /v0/workflows/{workflow_id} |  |
*DefaultApi* | [**v0WorkflowsWorkflowIdGet**](Apis/DefaultApi.md#v0workflowsworkflowidget) | **GET** /v0/workflows/{workflow_id} |  |


<a name="documentation-for-models"></a>
## Documentation for Models

 - [FindObject](./Models/FindObject.md)
 - [TaskDirectiveObject](./Models/TaskDirectiveObject.md)
 - [TaskforceObject](./Models/TaskforceObject.md)
 - [TaskforceObject_n_workers](./Models/TaskforceObject_n_workers.md)
 - [TaskforceObject_pilot_config](./Models/TaskforceObject_pilot_config.md)
 - [TaskforceObject_pilot_config_environment_value](./Models/TaskforceObject_pilot_config_environment_value.md)
 - [TaskforceObject_submit_dict_value](./Models/TaskforceObject_submit_dict_value.md)
 - [TaskforceObject_worker_config](./Models/TaskforceObject_worker_config.md)
 - [TaskforceUUIDObject](./Models/TaskforceUUIDObject.md)
 - [WorkflowObject](./Models/WorkflowObject.md)
 - [_v0__get_400_response](./Models/_v0__get_400_response.md)
 - [_v0_query_task_directives_post_200_response](./Models/_v0_query_task_directives_post_200_response.md)
 - [_v0_query_task_directives_post_400_response](./Models/_v0_query_task_directives_post_400_response.md)
 - [_v0_query_taskforces_post_200_response](./Models/_v0_query_taskforces_post_200_response.md)
 - [_v0_query_workflows_post_200_response](./Models/_v0_query_workflows_post_200_response.md)
 - [_v0_tms_condor_complete_taskforces__taskforce_uuid__post_request](./Models/_v0_tms_condor_complete_taskforces__taskforce_uuid__post_request.md)
 - [_v0_tms_pending_starter_taskforces_get_200_response](./Models/_v0_tms_pending_starter_taskforces_get_200_response.md)
 - [_v0_tms_statuses_taskforces_post_200_response](./Models/_v0_tms_statuses_taskforces_post_200_response.md)
 - [_v0_tms_statuses_taskforces_post_200_response_results_inner](./Models/_v0_tms_statuses_taskforces_post_200_response_results_inner.md)
 - [_v0_tms_statuses_taskforces_post_207_response](./Models/_v0_tms_statuses_taskforces_post_207_response.md)
 - [_v0_tms_statuses_taskforces_post_207_response_results_inner](./Models/_v0_tms_statuses_taskforces_post_207_response_results_inner.md)
 - [_v0_tms_statuses_taskforces_post_request](./Models/_v0_tms_statuses_taskforces_post_request.md)
 - [_v0_workflows__workflow_id__delete_200_response](./Models/_v0_workflows__workflow_id__delete_200_response.md)
 - [_v0_workflows_post_200_response](./Models/_v0_workflows_post_200_response.md)
 - [_v0_workflows_post_request](./Models/_v0_workflows_post_request.md)
 - [_v0_workflows_post_request_tasks_inner](./Models/_v0_workflows_post_request_tasks_inner.md)
 - [pilot_config](./Models/pilot_config.md)
 - [pilot_config_environment_value](./Models/pilot_config_environment_value.md)
 - [worker_config](./Models/worker_config.md)


<a name="documentation-for-authorization"></a>
## Documentation for Authorization

