<!--- Top of README Badges (automated) --->
[![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/Observation-Management-Service/ewms-workflow-management-service?include_prereleases)](https://github.com/Observation-Management-Service/ewms-workflow-management-service/) [![Lines of code](https://img.shields.io/tokei/lines/github/Observation-Management-Service/ewms-workflow-management-service)](https://github.com/Observation-Management-Service/ewms-workflow-management-service/) [![GitHub issues](https://img.shields.io/github/issues/Observation-Management-Service/ewms-workflow-management-service)](https://github.com/Observation-Management-Service/ewms-workflow-management-service/issues?q=is%3Aissue+sort%3Aupdated-desc+is%3Aopen) [![GitHub pull requests](https://img.shields.io/github/issues-pr/Observation-Management-Service/ewms-workflow-management-service)](https://github.com/Observation-Management-Service/ewms-workflow-management-service/pulls?q=is%3Apr+sort%3Aupdated-desc+is%3Aopen) 
<!--- End of README Badges (automated) --->
# ewms-workflow-management-service
The external interface for EWMS

<!--- Top of README openapi docs (automated) --->

<a name="documentation-for-api-endpoints"></a>
## Documentation for API Endpoints

All URIs are relative to *http://localhost*

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
*DefaultApi* | [**taskforcesTmsReportPost**](Apis/DefaultApi.md#taskforcestmsreportpost) | **POST** /taskforces/tms/report |  |


<a name="documentation-for-models"></a>
## Documentation for Models

 - [FindObject](./Models/FindObject.md)
 - [TaskDirectiveObject](./Models/TaskDirectiveObject.md)
 - [TaskforceObject](./Models/TaskforceObject.md)
 - [TaskforceObject_cluster_id](./Models/TaskforceObject_cluster_id.md)
 - [TaskforceObject_submit_dict_value](./Models/TaskforceObject_submit_dict_value.md)
 - [TaskforceUUIDObject](./Models/TaskforceUUIDObject.md)
 - [_schema_openapi_get_400_response](./Models/_schema_openapi_get_400_response.md)
 - [_task_directive__task_id__delete_200_response](./Models/_task_directive__task_id__delete_200_response.md)
 - [_task_directives_find_post_200_response](./Models/_task_directives_find_post_200_response.md)
 - [_taskforce_tms_action_pending_starter_get_200_response](./Models/_taskforce_tms_action_pending_starter_get_200_response.md)
 - [_taskforce_tms_condor_complete__taskforce_uuid__post_request](./Models/_taskforce_tms_condor_complete__taskforce_uuid__post_request.md)
 - [_taskforces_find_post_200_response](./Models/_taskforces_find_post_200_response.md)
 - [_taskforces_tms_report_post_200_response](./Models/_taskforces_tms_report_post_200_response.md)
 - [_taskforces_tms_report_post_207_response](./Models/_taskforces_tms_report_post_207_response.md)
 - [_taskforces_tms_report_post_request](./Models/_taskforces_tms_report_post_request.md)


<a name="documentation-for-authorization"></a>
## Documentation for Authorization

<!--- End of README openapi docs (automated) --->
