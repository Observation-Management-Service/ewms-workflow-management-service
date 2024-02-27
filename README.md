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
*DefaultApi* | [**tmsTaskforceCondorCompleteTaskforceUuidPost**](Apis/DefaultApi.md#tmstaskforcecondorcompletetaskforceuuidpost) | **POST** /tms/taskforce/condor-complete/{taskforce_uuid} |  |
*DefaultApi* | [**tmsTaskforcePendingGet**](Apis/DefaultApi.md#tmstaskforcependingget) | **GET** /taskforce/tms-action/pending |  |
*DefaultApi* | [**tmsTaskforceRunningTaskforceUuidPost**](Apis/DefaultApi.md#tmstaskforcerunningtaskforceuuidpost) | **POST** /taskforce/tms-action/condor-submit/{taskforce_uuid} |  |
*DefaultApi* | [**tmsTaskforceStopGet**](Apis/DefaultApi.md#tmstaskforcestopget) | **GET** /tms/taskforce/stop |  |
*DefaultApi* | [**tmsTaskforceStopTaskforceUuidDelete**](Apis/DefaultApi.md#tmstaskforcestoptaskforceuuiddelete) | **DELETE** /tms/taskforce/stop/{taskforce_uuid} |  |
*DefaultApi* | [**tmsTaskforceTaskforceUuidGet**](Apis/DefaultApi.md#tmstaskforcetaskforceuuidget) | **GET** /tms/taskforce/{taskforce_uuid} |  |
*DefaultApi* | [**tmsTaskforcesFindPost**](Apis/DefaultApi.md#tmstaskforcesfindpost) | **POST** /taskforces/find |  |
*DefaultApi* | [**tmsTaskforcesReportPost**](Apis/DefaultApi.md#tmstaskforcesreportpost) | **POST** /taskforces/tms/report |  |


<a name="documentation-for-models"></a>
## Documentation for Models

 - [FindObject](./Models/FindObject.md)
 - [TaskDirectiveObject](./Models/TaskDirectiveObject.md)
 - [TaskforceObject](./Models/TaskforceObject.md)
 - [TaskforceObject_cluster_id](./Models/TaskforceObject_cluster_id.md)
 - [TaskforceObject_submit_dict_value](./Models/TaskforceObject_submit_dict_value.md)
 - [TaskforceUUIDObject](./Models/TaskforceUUIDObject.md)
 - [_task_directive__task_id__delete_200_response](./Models/_task_directive__task_id__delete_200_response.md)
 - [_task_directives_find_post_200_response](./Models/_task_directives_find_post_200_response.md)
 - [_tms_taskforce_condor_complete__taskforce_uuid__post_request](./Models/_tms_taskforce_condor_complete__taskforce_uuid__post_request.md)
 - [_tms_taskforce_pending_get_200_response](./Models/_tms_taskforce_pending_get_200_response.md)
 - [_tms_taskforce_pending_get_400_response](./Models/_tms_taskforce_pending_get_400_response.md)
 - [_tms_taskforces_find_post_200_response](./Models/_tms_taskforces_find_post_200_response.md)
 - [_tms_taskforces_report_post_200_response](./Models/_tms_taskforces_report_post_200_response.md)
 - [_tms_taskforces_report_post_207_response](./Models/_tms_taskforces_report_post_207_response.md)
 - [_tms_taskforces_report_post_request](./Models/_tms_taskforces_report_post_request.md)


<a name="documentation-for-authorization"></a>
## Documentation for Authorization

<!--- End of README openapi docs (automated) --->
