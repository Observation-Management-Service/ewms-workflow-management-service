# DefaultApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**GET /v0/**](DefaultApi.md#get-v0) | **GET** /v0/ |  |
| [**POST /v0/query/task-directives**](DefaultApi.md#post-v0-query-task-directives) | **POST** /v0/query/task-directives |  |
| [**POST /v0/query/taskforces**](DefaultApi.md#post-v0-query-taskforces) | **POST** /v0/query/taskforces |  |
| [**POST /v0/query/workflows**](DefaultApi.md#post-v0-query-workflows) | **POST** /v0/query/workflows |  |
| [**GET /v0/schema/openapi**](DefaultApi.md#get-v0-schema-openapi) | **GET** /v0/schema/openapi |  |
| [**GET /v0/task-directives/{task_id}**](DefaultApi.md#get-v0-task-directives-task-id) | **GET** /v0/task-directives/{task_id} |  |
| [**GET /v0/taskforces/{taskforce_uuid}**](DefaultApi.md#get-v0-taskforces-taskforce-uuid) | **GET** /v0/taskforces/{taskforce_uuid} |  |
| [**POST /v0/tms/condor-complete/taskforces/{taskforce_uuid}**](DefaultApi.md#post-v0-tms-condor-complete-taskforces-taskforce-uuid) | **POST** /v0/tms/condor-complete/taskforces/{taskforce_uuid} |  |
| [**POST /v0/tms/condor-submit/taskforces/{taskforce_uuid}**](DefaultApi.md#post-v0-tms-condor-submit-taskforces-taskforce-uuid) | **POST** /v0/tms/condor-submit/taskforces/{taskforce_uuid} |  |
| [**GET /v0/tms/pending-starter/taskforces**](DefaultApi.md#get-v0-tms-pending-starter-taskforces) | **GET** /v0/tms/pending-starter/taskforces |  |
| [**GET /v0/tms/pending-stopper/taskforces**](DefaultApi.md#get-v0-tms-pending-stopper-taskforces) | **GET** /v0/tms/pending-stopper/taskforces |  |
| [**DELETE /v0/tms/pending-stopper/taskforces/{taskforce_uuid}**](DefaultApi.md#delete-v0-tms-pending-stopper-taskforces-taskforce-uuid) | **DELETE** /v0/tms/pending-stopper/taskforces/{taskforce_uuid} |  |
| [**POST /v0/tms/statuses/taskforces**](DefaultApi.md#post-v0-tms-statuses-taskforces) | **POST** /v0/tms/statuses/taskforces |  |
| [**POST /v0/workflows**](DefaultApi.md#post-v0-workflows) | **POST** /v0/workflows |  |
| [**DELETE /v0/workflows/{workflow_id}**](DefaultApi.md#delete-v0-workflows-workflow-id) | **DELETE** /v0/workflows/{workflow_id} |  |
| [**GET /v0/workflows/{workflow_id}**](DefaultApi.md#get-v0-workflows-workflow-id) | **GET** /v0/workflows/{workflow_id} |  |


<a name="GET /v0/"></a>
# **GET /v0/**
> GET /v0/()



### Parameters
This endpoint does not need any parameter.

### Return type

null (empty response body)

### Authorization


### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="POST /v0/query/task-directives"></a>
# **POST /v0/query/task-directives**
> _v0_query_task_directives_post_200_response POST /v0/query/task-directives(FindObject)



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

<a name="POST /v0/query/taskforces"></a>
# **POST /v0/query/taskforces**
> _v0_query_taskforces_post_200_response POST /v0/query/taskforces(FindObject)



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

<a name="POST /v0/query/workflows"></a>
# **POST /v0/query/workflows**
> _v0_query_workflows_post_200_response POST /v0/query/workflows(FindObject)



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

<a name="GET /v0/schema/openapi"></a>
# **GET /v0/schema/openapi**
> Map GET /v0/schema/openapi()



### Parameters
This endpoint does not need any parameter.

### Return type

[**Map**](../Models/AnyType.md)

### Authorization


### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="GET /v0/task-directives/{task_id}"></a>
# **GET /v0/task-directives/{task_id}**
> TaskDirectiveObject GET /v0/task-directives/{task_id}(task\_id)



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

<a name="GET /v0/taskforces/{taskforce_uuid}"></a>
# **GET /v0/taskforces/{taskforce_uuid}**
> TaskforceObject GET /v0/taskforces/{taskforce_uuid}(taskforce\_uuid)



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

<a name="POST /v0/tms/condor-complete/taskforces/{taskforce_uuid}"></a>
# **POST /v0/tms/condor-complete/taskforces/{taskforce_uuid}**
> TaskforceUUIDObject POST /v0/tms/condor-complete/taskforces/{taskforce_uuid}(taskforce\_uuid, \_v0\_tms\_condor\_complete\_taskforces\_\_taskforce\_uuid\_\_post\_request)



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

<a name="POST /v0/tms/condor-submit/taskforces/{taskforce_uuid}"></a>
# **POST /v0/tms/condor-submit/taskforces/{taskforce_uuid}**
> TaskforceUUIDObject POST /v0/tms/condor-submit/taskforces/{taskforce_uuid}(taskforce\_uuid, TaskforceObject)



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

<a name="GET /v0/tms/pending-starter/taskforces"></a>
# **GET /v0/tms/pending-starter/taskforces**
> _v0_tms_pending_starter_taskforces_get_200_response GET /v0/tms/pending-starter/taskforces(collector, schedd)



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

<a name="GET /v0/tms/pending-stopper/taskforces"></a>
# **GET /v0/tms/pending-stopper/taskforces**
> _v0_tms_pending_starter_taskforces_get_200_response GET /v0/tms/pending-stopper/taskforces(collector, schedd)



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

<a name="DELETE /v0/tms/pending-stopper/taskforces/{taskforce_uuid}"></a>
# **DELETE /v0/tms/pending-stopper/taskforces/{taskforce_uuid}**
> TaskforceUUIDObject DELETE /v0/tms/pending-stopper/taskforces/{taskforce_uuid}(taskforce\_uuid)



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

<a name="POST /v0/tms/statuses/taskforces"></a>
# **POST /v0/tms/statuses/taskforces**
> _v0_tms_statuses_taskforces_post_200_response POST /v0/tms/statuses/taskforces(\_v0\_tms\_statuses\_taskforces\_post\_request)



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

<a name="POST /v0/workflows"></a>
# **POST /v0/workflows**
> _v0_workflows_post_200_response POST /v0/workflows(\_v0\_workflows\_post\_request)



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

<a name="DELETE /v0/workflows/{workflow_id}"></a>
# **DELETE /v0/workflows/{workflow_id}**
> _v0_workflows__workflow_id__delete_200_response DELETE /v0/workflows/{workflow_id}(workflow\_id)



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

<a name="GET /v0/workflows/{workflow_id}"></a>
# **GET /v0/workflows/{workflow_id}**
> WorkflowObject GET /v0/workflows/{workflow_id}(workflow\_id)



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

