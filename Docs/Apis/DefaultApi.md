# DefaultApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**queryTaskDirectivesPost**](DefaultApi.md#queryTaskDirectivesPost) | **POST** /query/task-directives |  |
| [**queryTaskforcesPost**](DefaultApi.md#queryTaskforcesPost) | **POST** /query/taskforces |  |
| [**queryWorkflowsPost**](DefaultApi.md#queryWorkflowsPost) | **POST** /query/workflows |  |
| [**rootGet**](DefaultApi.md#rootGet) | **GET** / |  |
| [**schemaOpenapiGet**](DefaultApi.md#schemaOpenapiGet) | **GET** /schema/openapi |  |
| [**taskDirectivesTaskIdGet**](DefaultApi.md#taskDirectivesTaskIdGet) | **GET** /task-directives/{task_id} |  |
| [**taskforcesTaskforceUuidGet**](DefaultApi.md#taskforcesTaskforceUuidGet) | **GET** /taskforces/{taskforce_uuid} |  |
| [**tmsCondorCompleteTaskforcesTaskforceUuidPost**](DefaultApi.md#tmsCondorCompleteTaskforcesTaskforceUuidPost) | **POST** /tms/condor-complete/taskforces/{taskforce_uuid} |  |
| [**tmsCondorSubmitTaskforcesTaskforceUuidPost**](DefaultApi.md#tmsCondorSubmitTaskforcesTaskforceUuidPost) | **POST** /tms/condor-submit/taskforces/{taskforce_uuid} |  |
| [**tmsPendingStarterTaskforcesGet**](DefaultApi.md#tmsPendingStarterTaskforcesGet) | **GET** /tms/pending-starter/taskforces |  |
| [**tmsPendingStopperTaskforcesGet**](DefaultApi.md#tmsPendingStopperTaskforcesGet) | **GET** /tms/pending-stopper/taskforces |  |
| [**tmsPendingStopperTaskforcesTaskforceUuidDelete**](DefaultApi.md#tmsPendingStopperTaskforcesTaskforceUuidDelete) | **DELETE** /tms/pending-stopper/taskforces/{taskforce_uuid} |  |
| [**tmsStatusesTaskforcesPost**](DefaultApi.md#tmsStatusesTaskforcesPost) | **POST** /tms/statuses/taskforces |  |
| [**workflowsPost**](DefaultApi.md#workflowsPost) | **POST** /workflows |  |
| [**workflowsWorkflowIdDelete**](DefaultApi.md#workflowsWorkflowIdDelete) | **DELETE** /workflows/{workflow_id} |  |
| [**workflowsWorkflowIdGet**](DefaultApi.md#workflowsWorkflowIdGet) | **GET** /workflows/{workflow_id} |  |


<a name="queryTaskDirectivesPost"></a>
# **queryTaskDirectivesPost**
> _query_task_directives_post_200_response queryTaskDirectivesPost(FindObject)



### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **FindObject** | [**FindObject**](../Models/FindObject.md)|  | [optional] |

### Return type

[**_query_task_directives_post_200_response**](../Models/_query_task_directives_post_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="queryTaskforcesPost"></a>
# **queryTaskforcesPost**
> _query_taskforces_post_200_response queryTaskforcesPost(FindObject)



### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **FindObject** | [**FindObject**](../Models/FindObject.md)|  | [optional] |

### Return type

[**_query_taskforces_post_200_response**](../Models/_query_taskforces_post_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="queryWorkflowsPost"></a>
# **queryWorkflowsPost**
> _query_workflows_post_200_response queryWorkflowsPost(FindObject)



### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **FindObject** | [**FindObject**](../Models/FindObject.md)|  | [optional] |

### Return type

[**_query_workflows_post_200_response**](../Models/_query_workflows_post_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

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

<a name="taskDirectivesTaskIdGet"></a>
# **taskDirectivesTaskIdGet**
> TaskDirectiveObject taskDirectivesTaskIdGet(task\_id)



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

<a name="taskforcesTaskforceUuidGet"></a>
# **taskforcesTaskforceUuidGet**
> TaskforceObject taskforcesTaskforceUuidGet(taskforce\_uuid)



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

<a name="tmsCondorCompleteTaskforcesTaskforceUuidPost"></a>
# **tmsCondorCompleteTaskforcesTaskforceUuidPost**
> TaskforceUUIDObject tmsCondorCompleteTaskforcesTaskforceUuidPost(taskforce\_uuid, \_tms\_condor\_complete\_taskforces\_\_taskforce\_uuid\_\_post\_request)



### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **taskforce\_uuid** | **String**| the taskforce object&#39;s uuid | [default to null] |
| **\_tms\_condor\_complete\_taskforces\_\_taskforce\_uuid\_\_post\_request** | [**_tms_condor_complete_taskforces__taskforce_uuid__post_request**](../Models/_tms_condor_complete_taskforces__taskforce_uuid__post_request.md)|  | [optional] |

### Return type

[**TaskforceUUIDObject**](../Models/TaskforceUUIDObject.md)

### Authorization


### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="tmsCondorSubmitTaskforcesTaskforceUuidPost"></a>
# **tmsCondorSubmitTaskforcesTaskforceUuidPost**
> TaskforceUUIDObject tmsCondorSubmitTaskforcesTaskforceUuidPost(taskforce\_uuid, TaskforceObject)



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

<a name="tmsPendingStarterTaskforcesGet"></a>
# **tmsPendingStarterTaskforcesGet**
> _tms_pending_starter_taskforces_get_200_response tmsPendingStarterTaskforcesGet(collector, schedd)



### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **collector** | **String**| name of the condor collector | [default to null] |
| **schedd** | **String**| name of the condor schedd | [default to null] |

### Return type

[**_tms_pending_starter_taskforces_get_200_response**](../Models/_tms_pending_starter_taskforces_get_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="tmsPendingStopperTaskforcesGet"></a>
# **tmsPendingStopperTaskforcesGet**
> _tms_pending_starter_taskforces_get_200_response tmsPendingStopperTaskforcesGet(collector, schedd)



### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **collector** | **String**| name of the condor collector | [default to null] |
| **schedd** | **String**| name of the condor schedd | [default to null] |

### Return type

[**_tms_pending_starter_taskforces_get_200_response**](../Models/_tms_pending_starter_taskforces_get_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="tmsPendingStopperTaskforcesTaskforceUuidDelete"></a>
# **tmsPendingStopperTaskforcesTaskforceUuidDelete**
> TaskforceUUIDObject tmsPendingStopperTaskforcesTaskforceUuidDelete(taskforce\_uuid)



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

<a name="tmsStatusesTaskforcesPost"></a>
# **tmsStatusesTaskforcesPost**
> _tms_statuses_taskforces_post_200_response tmsStatusesTaskforcesPost(\_tms\_statuses\_taskforces\_post\_request)



### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **\_tms\_statuses\_taskforces\_post\_request** | [**_tms_statuses_taskforces_post_request**](../Models/_tms_statuses_taskforces_post_request.md)|  | [optional] |

### Return type

[**_tms_statuses_taskforces_post_200_response**](../Models/_tms_statuses_taskforces_post_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="workflowsPost"></a>
# **workflowsPost**
> _workflows_post_200_response workflowsPost(\_workflows\_post\_request)



### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **\_workflows\_post\_request** | [**_workflows_post_request**](../Models/_workflows_post_request.md)|  | [optional] |

### Return type

[**_workflows_post_200_response**](../Models/_workflows_post_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="workflowsWorkflowIdDelete"></a>
# **workflowsWorkflowIdDelete**
> _workflows__workflow_id__delete_200_response workflowsWorkflowIdDelete(workflow\_id)



### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **workflow\_id** | **String**| the id of the workflow object | [default to null] |

### Return type

[**_workflows__workflow_id__delete_200_response**](../Models/_workflows__workflow_id__delete_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="workflowsWorkflowIdGet"></a>
# **workflowsWorkflowIdGet**
> WorkflowObject workflowsWorkflowIdGet(workflow\_id)



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

