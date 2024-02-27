# DefaultApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**rootGet**](DefaultApi.md#rootGet) | **GET** / |  |
| [**schemaOpenapiGet**](DefaultApi.md#schemaOpenapiGet) | **GET** /schema/openapi |  |
| [**taskDirectivePost**](DefaultApi.md#taskDirectivePost) | **POST** /task/directive |  |
| [**taskDirectiveTaskIdDelete**](DefaultApi.md#taskDirectiveTaskIdDelete) | **DELETE** /task/directive/{task_id} |  |
| [**taskDirectiveTaskIdGet**](DefaultApi.md#taskDirectiveTaskIdGet) | **GET** /task/directive/{task_id} |  |
| [**taskDirectivesFindPost**](DefaultApi.md#taskDirectivesFindPost) | **POST** /task/directives/find |  |
| [**tmsTaskforceCondorCompleteTaskforceUuidPost**](DefaultApi.md#tmsTaskforceCondorCompleteTaskforceUuidPost) | **POST** /tms/taskforce/condor-complete/{taskforce_uuid} |  |
| [**tmsTaskforcePendingGet**](DefaultApi.md#tmsTaskforcePendingGet) | **GET** /tms/taskforce/pending |  |
| [**tmsTaskforceRunningTaskforceUuidPost**](DefaultApi.md#tmsTaskforceRunningTaskforceUuidPost) | **POST** /tms/taskforce/running/{taskforce_uuid} |  |
| [**tmsTaskforceStopGet**](DefaultApi.md#tmsTaskforceStopGet) | **GET** /tms/taskforce/stop |  |
| [**tmsTaskforceStopTaskforceUuidDelete**](DefaultApi.md#tmsTaskforceStopTaskforceUuidDelete) | **DELETE** /tms/taskforce/stop/{taskforce_uuid} |  |
| [**tmsTaskforceTaskforceUuidGet**](DefaultApi.md#tmsTaskforceTaskforceUuidGet) | **GET** /tms/taskforce/{taskforce_uuid} |  |
| [**tmsTaskforcesFindPost**](DefaultApi.md#tmsTaskforcesFindPost) | **POST** /taskforces/find |  |
| [**tmsTaskforcesReportPost**](DefaultApi.md#tmsTaskforcesReportPost) | **POST** /taskforces/tms/report |  |


<a name="rootGet"></a>
# **rootGet**
> rootGet()



### Parameters
This endpoint does not need any parameter.

### Return type

null (empty response body)

### Authorization


### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="schemaOpenapiGet"></a>
# **schemaOpenapiGet**
> Object schemaOpenapiGet()



### Parameters
This endpoint does not need any parameter.

### Return type

**Object**

### Authorization


### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="taskDirectivePost"></a>
# **taskDirectivePost**
> TaskDirectiveObject taskDirectivePost(TaskDirectiveObject)



### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **TaskDirectiveObject** | [**TaskDirectiveObject**](../Models/TaskDirectiveObject.md)|  | [optional] |

### Return type

[**TaskDirectiveObject**](../Models/TaskDirectiveObject.md)

### Authorization


### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="taskDirectiveTaskIdDelete"></a>
# **taskDirectiveTaskIdDelete**
> _task_directive__task_id__delete_200_response taskDirectiveTaskIdDelete(task\_id)



### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **task\_id** | **String**| the id of the task directive | [default to null] |

### Return type

[**_task_directive__task_id__delete_200_response**](../Models/_task_directive__task_id__delete_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="taskDirectiveTaskIdGet"></a>
# **taskDirectiveTaskIdGet**
> TaskDirectiveObject taskDirectiveTaskIdGet(task\_id)



### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **task\_id** | **String**| the id of the task directive | [default to null] |

### Return type

[**TaskDirectiveObject**](../Models/TaskDirectiveObject.md)

### Authorization


### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="taskDirectivesFindPost"></a>
# **taskDirectivesFindPost**
> _task_directives_find_post_200_response taskDirectivesFindPost(FindObject)



### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **FindObject** | [**FindObject**](../Models/FindObject.md)|  | [optional] |

### Return type

[**_task_directives_find_post_200_response**](../Models/_task_directives_find_post_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="tmsTaskforceCondorCompleteTaskforceUuidPost"></a>
# **tmsTaskforceCondorCompleteTaskforceUuidPost**
> TaskforceUUIDObject tmsTaskforceCondorCompleteTaskforceUuidPost(taskforce\_uuid, \_tms\_taskforce\_condor\_complete\_\_taskforce\_uuid\_\_post\_request)



### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **taskforce\_uuid** | **String**| the taskforce object&#39;s uuid | [default to null] |
| **\_tms\_taskforce\_condor\_complete\_\_taskforce\_uuid\_\_post\_request** | [**_tms_taskforce_condor_complete__taskforce_uuid__post_request**](../Models/_tms_taskforce_condor_complete__taskforce_uuid__post_request.md)|  | [optional] |

### Return type

[**TaskforceUUIDObject**](../Models/TaskforceUUIDObject.md)

### Authorization


### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="tmsTaskforcePendingGet"></a>
# **tmsTaskforcePendingGet**
> _tms_taskforce_pending_get_200_response tmsTaskforcePendingGet(collector, schedd)



### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **collector** | **String**| name of the condor collector | [default to null] |
| **schedd** | **String**| name of the condor schedd | [default to null] |

### Return type

[**_tms_taskforce_pending_get_200_response**](../Models/_tms_taskforce_pending_get_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="tmsTaskforceRunningTaskforceUuidPost"></a>
# **tmsTaskforceRunningTaskforceUuidPost**
> TaskforceUUIDObject tmsTaskforceRunningTaskforceUuidPost(taskforce\_uuid, TaskforceObject)



### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **taskforce\_uuid** | **String**| the taskforce object&#39;s uuid | [default to null] |
| **TaskforceObject** | [**TaskforceObject**](../Models/TaskforceObject.md)|  | [optional] |

### Return type

[**TaskforceUUIDObject**](../Models/TaskforceUUIDObject.md)

### Authorization


### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="tmsTaskforceStopGet"></a>
# **tmsTaskforceStopGet**
> _tms_taskforce_pending_get_200_response tmsTaskforceStopGet(collector, schedd)



### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **collector** | **String**| name of the condor collector | [default to null] |
| **schedd** | **String**| name of the condor schedd | [default to null] |

### Return type

[**_tms_taskforce_pending_get_200_response**](../Models/_tms_taskforce_pending_get_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="tmsTaskforceStopTaskforceUuidDelete"></a>
# **tmsTaskforceStopTaskforceUuidDelete**
> TaskforceUUIDObject tmsTaskforceStopTaskforceUuidDelete(taskforce\_uuid)



### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **taskforce\_uuid** | **String**| the taskforce object&#39;s uuid | [default to null] |

### Return type

[**TaskforceUUIDObject**](../Models/TaskforceUUIDObject.md)

### Authorization


### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="tmsTaskforceTaskforceUuidGet"></a>
# **tmsTaskforceTaskforceUuidGet**
> TaskforceObject tmsTaskforceTaskforceUuidGet(taskforce\_uuid)



### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **taskforce\_uuid** | **String**| the taskforce object&#39;s uuid | [default to null] |

### Return type

[**TaskforceObject**](../Models/TaskforceObject.md)

### Authorization


### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="tmsTaskforcesFindPost"></a>
# **tmsTaskforcesFindPost**
> _tms_taskforces_find_post_200_response tmsTaskforcesFindPost(FindObject)



### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **FindObject** | [**FindObject**](../Models/FindObject.md)|  | [optional] |

### Return type

[**_tms_taskforces_find_post_200_response**](../Models/_tms_taskforces_find_post_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="tmsTaskforcesReportPost"></a>
# **tmsTaskforcesReportPost**
> _tms_taskforces_report_post_200_response tmsTaskforcesReportPost(\_tms\_taskforces\_report\_post\_request)



### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **\_tms\_taskforces\_report\_post\_request** | [**_tms_taskforces_report_post_request**](../Models/_tms_taskforces_report_post_request.md)|  | [optional] |

### Return type

[**_tms_taskforces_report_post_200_response**](../Models/_tms_taskforces_report_post_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

