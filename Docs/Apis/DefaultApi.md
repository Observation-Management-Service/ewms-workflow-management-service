# DefaultApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**v0Get**](DefaultApi.md#v0Get) | **GET** /v0/ |  |
| [**v0QueryTaskDirectivesPost**](DefaultApi.md#v0QueryTaskDirectivesPost) | **POST** /v0/query/task-directives |  |
| [**v0QueryTaskforcesPost**](DefaultApi.md#v0QueryTaskforcesPost) | **POST** /v0/query/taskforces |  |
| [**v0QueryWorkflowsPost**](DefaultApi.md#v0QueryWorkflowsPost) | **POST** /v0/query/workflows |  |
| [**v0SchemaOpenapiGet**](DefaultApi.md#v0SchemaOpenapiGet) | **GET** /v0/schema/openapi |  |
| [**v0TaskDirectivesTaskIdGet**](DefaultApi.md#v0TaskDirectivesTaskIdGet) | **GET** /v0/task-directives/{task_id} |  |
| [**v0TaskforcesTaskforceUuidGet**](DefaultApi.md#v0TaskforcesTaskforceUuidGet) | **GET** /v0/taskforces/{taskforce_uuid} |  |
| [**v0TmsCondorCompleteTaskforcesTaskforceUuidPost**](DefaultApi.md#v0TmsCondorCompleteTaskforcesTaskforceUuidPost) | **POST** /v0/tms/condor-complete/taskforces/{taskforce_uuid} |  |
| [**v0TmsCondorSubmitTaskforcesTaskforceUuidPost**](DefaultApi.md#v0TmsCondorSubmitTaskforcesTaskforceUuidPost) | **POST** /v0/tms/condor-submit/taskforces/{taskforce_uuid} |  |
| [**v0TmsPendingStarterTaskforcesGet**](DefaultApi.md#v0TmsPendingStarterTaskforcesGet) | **GET** /v0/tms/pending-starter/taskforces |  |
| [**v0TmsPendingStopperTaskforcesGet**](DefaultApi.md#v0TmsPendingStopperTaskforcesGet) | **GET** /v0/tms/pending-stopper/taskforces |  |
| [**v0TmsPendingStopperTaskforcesTaskforceUuidDelete**](DefaultApi.md#v0TmsPendingStopperTaskforcesTaskforceUuidDelete) | **DELETE** /v0/tms/pending-stopper/taskforces/{taskforce_uuid} |  |
| [**v0TmsStatusesTaskforcesPost**](DefaultApi.md#v0TmsStatusesTaskforcesPost) | **POST** /v0/tms/statuses/taskforces |  |
| [**v0WorkflowsPost**](DefaultApi.md#v0WorkflowsPost) | **POST** /v0/workflows |  |
| [**v0WorkflowsWorkflowIdDelete**](DefaultApi.md#v0WorkflowsWorkflowIdDelete) | **DELETE** /v0/workflows/{workflow_id} |  |
| [**v0WorkflowsWorkflowIdGet**](DefaultApi.md#v0WorkflowsWorkflowIdGet) | **GET** /v0/workflows/{workflow_id} |  |


<a name="v0Get"></a>
# **v0Get**
> v0Get()



### Parameters
This endpoint does not need any parameter.

### Return type

null (empty response body)

### Authorization


### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="v0QueryTaskDirectivesPost"></a>
# **v0QueryTaskDirectivesPost**
> _v0_query_task_directives_post_200_response v0QueryTaskDirectivesPost(FindObject)



### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **FindObject** | [**FindObject**](../Models/FindObject.md)|  | [optional] |

### Return type

[**_v0_query_task_directives_post_200_response**](../Models/_v0_query_task_directives_post_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="v0QueryTaskforcesPost"></a>
# **v0QueryTaskforcesPost**
> _v0_query_taskforces_post_200_response v0QueryTaskforcesPost(FindObject)



### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **FindObject** | [**FindObject**](../Models/FindObject.md)|  | [optional] |

### Return type

[**_v0_query_taskforces_post_200_response**](../Models/_v0_query_taskforces_post_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="v0QueryWorkflowsPost"></a>
# **v0QueryWorkflowsPost**
> _v0_query_workflows_post_200_response v0QueryWorkflowsPost(FindObject)



### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **FindObject** | [**FindObject**](../Models/FindObject.md)|  | [optional] |

### Return type

[**_v0_query_workflows_post_200_response**](../Models/_v0_query_workflows_post_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="v0SchemaOpenapiGet"></a>
# **v0SchemaOpenapiGet**
> Object v0SchemaOpenapiGet()



### Parameters
This endpoint does not need any parameter.

### Return type

**Object**

### Authorization


### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="v0TaskDirectivesTaskIdGet"></a>
# **v0TaskDirectivesTaskIdGet**
> TaskDirectiveObject v0TaskDirectivesTaskIdGet(task\_id)



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

<a name="v0TaskforcesTaskforceUuidGet"></a>
# **v0TaskforcesTaskforceUuidGet**
> TaskforceObject v0TaskforcesTaskforceUuidGet(taskforce\_uuid)



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

<a name="v0TmsCondorCompleteTaskforcesTaskforceUuidPost"></a>
# **v0TmsCondorCompleteTaskforcesTaskforceUuidPost**
> TaskforceUUIDObject v0TmsCondorCompleteTaskforcesTaskforceUuidPost(taskforce\_uuid, \_v0\_tms\_condor\_complete\_taskforces\_\_taskforce\_uuid\_\_post\_request)



### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **taskforce\_uuid** | **String**| the taskforce object&#39;s uuid | [default to null] |
| **\_v0\_tms\_condor\_complete\_taskforces\_\_taskforce\_uuid\_\_post\_request** | [**_v0_tms_condor_complete_taskforces__taskforce_uuid__post_request**](../Models/_v0_tms_condor_complete_taskforces__taskforce_uuid__post_request.md)|  | [optional] |

### Return type

[**TaskforceUUIDObject**](../Models/TaskforceUUIDObject.md)

### Authorization


### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="v0TmsCondorSubmitTaskforcesTaskforceUuidPost"></a>
# **v0TmsCondorSubmitTaskforcesTaskforceUuidPost**
> TaskforceUUIDObject v0TmsCondorSubmitTaskforcesTaskforceUuidPost(taskforce\_uuid, TaskforceObject)



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

<a name="v0TmsPendingStarterTaskforcesGet"></a>
# **v0TmsPendingStarterTaskforcesGet**
> _v0_tms_pending_starter_taskforces_get_200_response v0TmsPendingStarterTaskforcesGet(collector, schedd)



### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **collector** | **String**| name of the condor collector | [default to null] |
| **schedd** | **String**| name of the condor schedd | [default to null] |

### Return type

[**_v0_tms_pending_starter_taskforces_get_200_response**](../Models/_v0_tms_pending_starter_taskforces_get_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="v0TmsPendingStopperTaskforcesGet"></a>
# **v0TmsPendingStopperTaskforcesGet**
> _v0_tms_pending_starter_taskforces_get_200_response v0TmsPendingStopperTaskforcesGet(collector, schedd)



### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **collector** | **String**| name of the condor collector | [default to null] |
| **schedd** | **String**| name of the condor schedd | [default to null] |

### Return type

[**_v0_tms_pending_starter_taskforces_get_200_response**](../Models/_v0_tms_pending_starter_taskforces_get_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="v0TmsPendingStopperTaskforcesTaskforceUuidDelete"></a>
# **v0TmsPendingStopperTaskforcesTaskforceUuidDelete**
> TaskforceUUIDObject v0TmsPendingStopperTaskforcesTaskforceUuidDelete(taskforce\_uuid)



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

<a name="v0TmsStatusesTaskforcesPost"></a>
# **v0TmsStatusesTaskforcesPost**
> _v0_tms_statuses_taskforces_post_200_response v0TmsStatusesTaskforcesPost(\_v0\_tms\_statuses\_taskforces\_post\_request)



### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **\_v0\_tms\_statuses\_taskforces\_post\_request** | [**_v0_tms_statuses_taskforces_post_request**](../Models/_v0_tms_statuses_taskforces_post_request.md)|  | [optional] |

### Return type

[**_v0_tms_statuses_taskforces_post_200_response**](../Models/_v0_tms_statuses_taskforces_post_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="v0WorkflowsPost"></a>
# **v0WorkflowsPost**
> _v0_workflows_post_200_response v0WorkflowsPost(\_v0\_workflows\_post\_request)



### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **\_v0\_workflows\_post\_request** | [**_v0_workflows_post_request**](../Models/_v0_workflows_post_request.md)|  | [optional] |

### Return type

[**_v0_workflows_post_200_response**](../Models/_v0_workflows_post_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="v0WorkflowsWorkflowIdDelete"></a>
# **v0WorkflowsWorkflowIdDelete**
> _v0_workflows__workflow_id__delete_200_response v0WorkflowsWorkflowIdDelete(workflow\_id)



### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **workflow\_id** | **String**| the id of the workflow object | [default to null] |

### Return type

[**_v0_workflows__workflow_id__delete_200_response**](../Models/_v0_workflows__workflow_id__delete_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="v0WorkflowsWorkflowIdGet"></a>
# **v0WorkflowsWorkflowIdGet**
> WorkflowObject v0WorkflowsWorkflowIdGet(workflow\_id)



### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **workflow\_id** | **String**| the id of the workflow object | [default to null] |

### Return type

[**WorkflowObject**](../Models/WorkflowObject.md)

### Authorization


### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

