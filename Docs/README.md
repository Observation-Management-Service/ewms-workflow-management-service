# Documentation for EWMS - Workflow Management Service

<a name="documentation-for-api-endpoints"></a>
## Documentation for API Endpoints


| Class | Method | HTTP request | Description |
|------------ | ------------- | ------------- | -------------|
| *DefaultApi* | [**rootGet**](Apis/DefaultApi.md#rootget) | **GET** / |  |
*DefaultApi* | [**schemaOpenapiGet**](Apis/DefaultApi.md#schemaopenapiget) | **GET** /schema/openapi |  |
*DefaultApi* | [**taskDirectivePost**](Apis/DefaultApi.md#taskdirectivepost) | **POST** /task/directive |  |
*DefaultApi* | [**taskDirectiveTaskIdDelete**](Apis/DefaultApi.md#taskdirectivetaskiddelete) | **DELETE** /task/directive/{task_id} |  |
*DefaultApi* | [**taskDirectiveTaskIdGet**](Apis/DefaultApi.md#taskdirectivetaskidget) | **GET** /task/directive/{task_id} |  |
*DefaultApi* | [**taskDirectivesFindPost**](Apis/DefaultApi.md#taskdirectivesfindpost) | **POST** /task/directives/find |  |
*DefaultApi* | [**taskforceTaskforceUuidGet**](Apis/DefaultApi.md#taskforcetaskforceuuidget) | **GET** /taskforce/{taskforce_uuid} |  |
*DefaultApi* | [**taskforceTmsActionCondorSubmitTaskforceUuidPost**](Apis/DefaultApi.md#taskforcetmsactioncondorsubmittaskforceuuidpost) | **POST** /taskforce/tms-action/condor-submit/{taskforce_uuid} |  |
*DefaultApi* | [**taskforceTmsActionPendingStarterGet**](Apis/DefaultApi.md#taskforcetmsactionpendingstarterget) | **GET** /taskforce/tms-action/pending-starter |  |
*DefaultApi* | [**taskforceTmsActionPendingStopperGet**](Apis/DefaultApi.md#taskforcetmsactionpendingstopperget) | **GET** /taskforce/tms-action/pending-stopper |  |
*DefaultApi* | [**taskforceTmsActionPendingStopperTaskforceUuidDelete**](Apis/DefaultApi.md#taskforcetmsactionpendingstoppertaskforceuuiddelete) | **DELETE** /taskforce/tms-action/pending-stopper/{taskforce_uuid} |  |
*DefaultApi* | [**taskforceTmsCondorCompleteTaskforceUuidPost**](Apis/DefaultApi.md#taskforcetmscondorcompletetaskforceuuidpost) | **POST** /taskforce/tms/condor-complete/{taskforce_uuid} |  |
*DefaultApi* | [**taskforcesFindPost**](Apis/DefaultApi.md#taskforcesfindpost) | **POST** /taskforces/find |  |
*DefaultApi* | [**taskforcesTmsStatusPost**](Apis/DefaultApi.md#taskforcestmsstatuspost) | **POST** /taskforces/tms/status |  |


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
 - [__get_400_response](./Models/__get_400_response.md)
 - [_schema_openapi_get_400_response](./Models/_schema_openapi_get_400_response.md)
 - [_task_directive__task_id__delete_200_response](./Models/_task_directive__task_id__delete_200_response.md)
 - [_task_directive_post_request](./Models/_task_directive_post_request.md)
 - [_task_directives_find_post_200_response](./Models/_task_directives_find_post_200_response.md)
 - [_taskforce_tms_action_pending_starter_get_200_response](./Models/_taskforce_tms_action_pending_starter_get_200_response.md)
 - [_taskforce_tms_condor_complete__taskforce_uuid__post_request](./Models/_taskforce_tms_condor_complete__taskforce_uuid__post_request.md)
 - [_taskforces_find_post_200_response](./Models/_taskforces_find_post_200_response.md)
 - [_taskforces_tms_status_post_200_response](./Models/_taskforces_tms_status_post_200_response.md)
 - [_taskforces_tms_status_post_200_response_results_inner](./Models/_taskforces_tms_status_post_200_response_results_inner.md)
 - [_taskforces_tms_status_post_207_response](./Models/_taskforces_tms_status_post_207_response.md)
 - [_taskforces_tms_status_post_207_response_results_inner](./Models/_taskforces_tms_status_post_207_response_results_inner.md)
 - [_taskforces_tms_status_post_request](./Models/_taskforces_tms_status_post_request.md)
 - [worker_config](./Models/worker_config.md)


<a name="documentation-for-authorization"></a>
## Documentation for Authorization

