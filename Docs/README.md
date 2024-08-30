# Documentation for EWMS - Workflow Management Service

<a name="documentation-for-api-endpoints"></a>
## Documentation for API Endpoints


| Class | Method | HTTP request | Description |
|------------ | ------------- | ------------- | -------------|
| *DefaultApi* | [**GET /v0/**](Apis/DefaultApi.md#get-v0) | **GET** /v0/ |  |
*DefaultApi* | [**POST /v0/query/task-directives**](Apis/DefaultApi.md#post-v0-query-task-directives) | **POST** /v0/query/task-directives |  |
*DefaultApi* | [**POST /v0/query/taskforces**](Apis/DefaultApi.md#post-v0-query-taskforces) | **POST** /v0/query/taskforces |  |
*DefaultApi* | [**POST /v0/query/workflows**](Apis/DefaultApi.md#post-v0-query-workflows) | **POST** /v0/query/workflows |  |
*DefaultApi* | [**GET /v0/schema/openapi**](Apis/DefaultApi.md#get-v0-schema-openapi) | **GET** /v0/schema/openapi |  |
*DefaultApi* | [**GET /v0/task-directives/{task_id}**](Apis/DefaultApi.md#get-v0-task-directives-task-id) | **GET** /v0/task-directives/{task_id} |  |
*DefaultApi* | [**GET /v0/taskforces/{taskforce_uuid}**](Apis/DefaultApi.md#get-v0-taskforces-taskforce-uuid) | **GET** /v0/taskforces/{taskforce_uuid} |  |
*DefaultApi* | [**POST /v0/tms/condor-complete/taskforces/{taskforce_uuid}**](Apis/DefaultApi.md#post-v0-tms-condor-complete-taskforces-taskforce-uuid) | **POST** /v0/tms/condor-complete/taskforces/{taskforce_uuid} |  |
*DefaultApi* | [**POST /v0/tms/condor-submit/taskforces/{taskforce_uuid}**](Apis/DefaultApi.md#post-v0-tms-condor-submit-taskforces-taskforce-uuid) | **POST** /v0/tms/condor-submit/taskforces/{taskforce_uuid} |  |
*DefaultApi* | [**GET /v0/tms/pending-starter/taskforces**](Apis/DefaultApi.md#get-v0-tms-pending-starter-taskforces) | **GET** /v0/tms/pending-starter/taskforces |  |
*DefaultApi* | [**GET /v0/tms/pending-stopper/taskforces**](Apis/DefaultApi.md#get-v0-tms-pending-stopper-taskforces) | **GET** /v0/tms/pending-stopper/taskforces |  |
*DefaultApi* | [**DELETE /v0/tms/pending-stopper/taskforces/{taskforce_uuid}**](Apis/DefaultApi.md#delete-v0-tms-pending-stopper-taskforces-taskforce-uuid) | **DELETE** /v0/tms/pending-stopper/taskforces/{taskforce_uuid} |  |
*DefaultApi* | [**POST /v0/tms/statuses/taskforces**](Apis/DefaultApi.md#post-v0-tms-statuses-taskforces) | **POST** /v0/tms/statuses/taskforces |  |
*DefaultApi* | [**POST /v0/workflows**](Apis/DefaultApi.md#post-v0-workflows) | **POST** /v0/workflows |  |
*DefaultApi* | [**DELETE /v0/workflows/{workflow_id}**](Apis/DefaultApi.md#delete-v0-workflows-workflow-id) | **DELETE** /v0/workflows/{workflow_id} |  |
*DefaultApi* | [**GET /v0/workflows/{workflow_id}**](Apis/DefaultApi.md#get-v0-workflows-workflow-id) | **GET** /v0/workflows/{workflow_id} |  |


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

