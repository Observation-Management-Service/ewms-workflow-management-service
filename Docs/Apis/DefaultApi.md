# DefaultApi


| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [_details_](DefaultApi.md#get-v1) | **GET** /v1/ |  |
| [_details_](DefaultApi.md#post-v1querytask-directives) | **POST** /v1/query/task-directives |  |
| [_details_](DefaultApi.md#post-v1querytaskforces) | **POST** /v1/query/taskforces |  |
| [_details_](DefaultApi.md#post-v1queryworkflows) | **POST** /v1/query/workflows |  |
| [_details_](DefaultApi.md#get-v1schemaopenapi) | **GET** /v1/schema/openapi |  |
| [_details_](DefaultApi.md#post-v1task-directivestask_idactionsadd-workers) | **POST** /v1/task-directives/{task_id}/actions/add-workers |  |
| [_details_](DefaultApi.md#get-v1task-directivestask_id) | **GET** /v1/task-directives/{task_id} |  |
| [_details_](DefaultApi.md#get-v1taskforcestaskforce_uuid) | **GET** /v1/taskforces/{taskforce_uuid} |  |
| [_details_](DefaultApi.md#post-v1tmscondor-completetaskforcestaskforce_uuid) | **POST** /v1/tms/condor-complete/taskforces/{taskforce_uuid} |  |
| [_details_](DefaultApi.md#post-v1tmscondor-rmtaskforcestaskforce_uuidfailed) | **POST** /v1/tms/condor-rm/taskforces/{taskforce_uuid}/failed |  |
| [_details_](DefaultApi.md#post-v1tmscondor-rmtaskforcestaskforce_uuid) | **POST** /v1/tms/condor-rm/taskforces/{taskforce_uuid} |  |
| [_details_](DefaultApi.md#post-v1tmscondor-submittaskforcestaskforce_uuidfailed) | **POST** /v1/tms/condor-submit/taskforces/{taskforce_uuid}/failed |  |
| [_details_](DefaultApi.md#post-v1tmscondor-submittaskforcestaskforce_uuid) | **POST** /v1/tms/condor-submit/taskforces/{taskforce_uuid} |  |
| [_details_](DefaultApi.md#get-v1tmspending-startertaskforces) | **GET** /v1/tms/pending-starter/taskforces |  |
| [_details_](DefaultApi.md#get-v1tmspending-stoppertaskforces) | **GET** /v1/tms/pending-stopper/taskforces |  |
| [_details_](DefaultApi.md#post-v1tmsstatusestaskforces) | **POST** /v1/tms/statuses/taskforces |  |
| [_details_](DefaultApi.md#post-v1workflows) | **POST** /v1/workflows |  |
| [_details_](DefaultApi.md#post-v1workflowsworkflow_idactionsabort) | **POST** /v1/workflows/{workflow_id}/actions/abort |  |
| [_details_](DefaultApi.md#post-v1workflowsworkflow_idactionsfinished) | **POST** /v1/workflows/{workflow_id}/actions/finished |  |
| [_details_](DefaultApi.md#get-v1workflowsworkflow_id) | **GET** /v1/workflows/{workflow_id} |  |


<a name="GET /v1/"></a>
# **GET /v1/**
> GET /v1/()



    Returns an empty response.

### Parameters
This endpoint does not need any parameter.

### Return type

null (empty response body)

### Authorization


### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="POST /v1/query/task-directives"></a>
# **POST /v1/query/task-directives**
> _v1_query_task_directives_post_200_response POST /v1/query/task-directives(FindObject)



    Queries and returns a list of task directive objects based on the provided criteria.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **FindObject** | [**FindObject**](../Models/FindObject.md)|  | [optional] |

### Return type

[**_v1_query_task_directives_post_200_response**](../Models/_v1_query_task_directives_post_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="POST /v1/query/taskforces"></a>
# **POST /v1/query/taskforces**
> _v1_query_taskforces_post_200_response POST /v1/query/taskforces(FindObject)



    Queries and returns a list of taskforce objects based on the provided criteria.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **FindObject** | [**FindObject**](../Models/FindObject.md)|  | [optional] |

### Return type

[**_v1_query_taskforces_post_200_response**](../Models/_v1_query_taskforces_post_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="POST /v1/query/workflows"></a>
# **POST /v1/query/workflows**
> _v1_query_workflows_post_200_response POST /v1/query/workflows(FindObject)



    Queries and returns a list of workflow objects based on the provided criteria.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **FindObject** | [**FindObject**](../Models/FindObject.md)|  | [optional] |

### Return type

[**_v1_query_workflows_post_200_response**](../Models/_v1_query_workflows_post_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="GET /v1/schema/openapi"></a>
# **GET /v1/schema/openapi**
> Object GET /v1/schema/openapi()



    Returns the OpenAPI schema.

### Parameters
This endpoint does not need any parameter.

### Return type

**Object**

### Authorization


### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="POST /v1/task-directives/{task_id}/actions/add-workers"></a>
# **POST /v1/task-directives/{task_id}/actions/add-workers**
> TaskforceObject POST /v1/task-directives/{task_id}/actions/add-workers(task\_id, \_v1\_task\_directives\_\_task\_id\_\_actions\_add\_workers\_post\_request)



    Creates a new taskforce (and associated workers) for an existing task directive.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **task\_id** | **String**| The ID of the task directive to which the taskforce (and workers) will be added. | [default to null] |
| **\_v1\_task\_directives\_\_task\_id\_\_actions\_add\_workers\_post\_request** | [**_v1_task_directives__task_id__actions_add_workers_post_request**](../Models/_v1_task_directives__task_id__actions_add_workers_post_request.md)|  | [optional] |

### Return type

[**TaskforceObject**](../Models/TaskforceObject.md)

### Authorization


### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="GET /v1/task-directives/{task_id}"></a>
# **GET /v1/task-directives/{task_id}**
> TaskDirectiveObject GET /v1/task-directives/{task_id}(task\_id)



    Retrieves the task directive that matches the specified task ID.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **task\_id** | **String**| The ID of the task directive | [default to null] |

### Return type

[**TaskDirectiveObject**](../Models/TaskDirectiveObject.md)

### Authorization


### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="GET /v1/taskforces/{taskforce_uuid}"></a>
# **GET /v1/taskforces/{taskforce_uuid}**
> TaskforceObject GET /v1/taskforces/{taskforce_uuid}(taskforce\_uuid)



    Retrieves the taskforce object that matches the specified taskforce UUID.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **taskforce\_uuid** | **String**| uuid of the taskforce | [default to null] |

### Return type

[**TaskforceObject**](../Models/TaskforceObject.md)

### Authorization


### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="POST /v1/tms/condor-complete/taskforces/{taskforce_uuid}"></a>
# **POST /v1/tms/condor-complete/taskforces/{taskforce_uuid}**
> _v1_tms_condor_complete_taskforces__taskforce_uuid__post_200_response POST /v1/tms/condor-complete/taskforces/{taskforce_uuid}(taskforce\_uuid, \_v1\_tms\_condor\_complete\_taskforces\_\_taskforce\_uuid\_\_post\_request)



    For internal use only (TMS): Updates the specified taskforce with the completion timestamp of the HTCondor cluster.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **taskforce\_uuid** | **String**| uuid of the taskforce | [default to null] |
| **\_v1\_tms\_condor\_complete\_taskforces\_\_taskforce\_uuid\_\_post\_request** | [**_v1_tms_condor_complete_taskforces__taskforce_uuid__post_request**](../Models/_v1_tms_condor_complete_taskforces__taskforce_uuid__post_request.md)|  | [optional] |

### Return type

[**_v1_tms_condor_complete_taskforces__taskforce_uuid__post_200_response**](../Models/_v1_tms_condor_complete_taskforces__taskforce_uuid__post_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="POST /v1/tms/condor-rm/taskforces/{taskforce_uuid}/failed"></a>
# **POST /v1/tms/condor-rm/taskforces/{taskforce_uuid}/failed**
> _v1_tms_condor_complete_taskforces__taskforce_uuid__post_200_response POST /v1/tms/condor-rm/taskforces/{taskforce_uuid}/failed(taskforce\_uuid, \_v1\_tms\_condor\_rm\_taskforces\_\_taskforce\_uuid\_\_failed\_post\_request)



    For internal use only (TMS): Communicates that a taskforce failed to be removed on HTCondor.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **taskforce\_uuid** | **String**| uuid of the taskforce | [default to null] |
| **\_v1\_tms\_condor\_rm\_taskforces\_\_taskforce\_uuid\_\_failed\_post\_request** | [**_v1_tms_condor_rm_taskforces__taskforce_uuid__failed_post_request**](../Models/_v1_tms_condor_rm_taskforces__taskforce_uuid__failed_post_request.md)|  | [optional] |

### Return type

[**_v1_tms_condor_complete_taskforces__taskforce_uuid__post_200_response**](../Models/_v1_tms_condor_complete_taskforces__taskforce_uuid__post_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="POST /v1/tms/condor-rm/taskforces/{taskforce_uuid}"></a>
# **POST /v1/tms/condor-rm/taskforces/{taskforce_uuid}**
> _v1_tms_condor_complete_taskforces__taskforce_uuid__post_200_response POST /v1/tms/condor-rm/taskforces/{taskforce_uuid}(taskforce\_uuid)



    For internal use only (TMS): Confirms that a taskforce has been removed on HTCondor.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **taskforce\_uuid** | **String**| uuid of the taskforce | [default to null] |

### Return type

[**_v1_tms_condor_complete_taskforces__taskforce_uuid__post_200_response**](../Models/_v1_tms_condor_complete_taskforces__taskforce_uuid__post_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="POST /v1/tms/condor-submit/taskforces/{taskforce_uuid}/failed"></a>
# **POST /v1/tms/condor-submit/taskforces/{taskforce_uuid}/failed**
> _v1_tms_condor_complete_taskforces__taskforce_uuid__post_200_response POST /v1/tms/condor-submit/taskforces/{taskforce_uuid}/failed(taskforce\_uuid, \_v1\_tms\_condor\_submit\_taskforces\_\_taskforce\_uuid\_\_failed\_post\_request)



    For internal use only (TMS): Communicates that a taskforce failed to be submitted to HTCondor for execution.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **taskforce\_uuid** | **String**| uuid of the taskforce | [default to null] |
| **\_v1\_tms\_condor\_submit\_taskforces\_\_taskforce\_uuid\_\_failed\_post\_request** | [**_v1_tms_condor_submit_taskforces__taskforce_uuid__failed_post_request**](../Models/_v1_tms_condor_submit_taskforces__taskforce_uuid__failed_post_request.md)|  | [optional] |

### Return type

[**_v1_tms_condor_complete_taskforces__taskforce_uuid__post_200_response**](../Models/_v1_tms_condor_complete_taskforces__taskforce_uuid__post_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="POST /v1/tms/condor-submit/taskforces/{taskforce_uuid}"></a>
# **POST /v1/tms/condor-submit/taskforces/{taskforce_uuid}**
> _v1_tms_condor_complete_taskforces__taskforce_uuid__post_200_response POST /v1/tms/condor-submit/taskforces/{taskforce_uuid}(taskforce\_uuid, TaskforceObject)



    For internal use only (TMS): Confirms that a taskforce has been submitted to HTCondor for execution.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **taskforce\_uuid** | **String**| uuid of the taskforce | [default to null] |
| **TaskforceObject** | [**TaskforceObject**](../Models/TaskforceObject.md)|  | [optional] |

### Return type

[**_v1_tms_condor_complete_taskforces__taskforce_uuid__post_200_response**](../Models/_v1_tms_condor_complete_taskforces__taskforce_uuid__post_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="GET /v1/tms/pending-starter/taskforces"></a>
# **GET /v1/tms/pending-starter/taskforces**
> _v1_tms_pending_starter_taskforces_get_200_response GET /v1/tms/pending-starter/taskforces(schedd, collector)



    For internal use only (TMS): Retrieves the next taskforce ready to start at the specified HTCondor location.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **schedd** | **String**| name of the condor schedd | [default to null] |
| **collector** | **String**| DEPRECATED: name of the condor collector -- no longer used/needed | [optional] [default to null] |

### Return type

[**_v1_tms_pending_starter_taskforces_get_200_response**](../Models/_v1_tms_pending_starter_taskforces_get_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="GET /v1/tms/pending-stopper/taskforces"></a>
# **GET /v1/tms/pending-stopper/taskforces**
> _v1_tms_pending_stopper_taskforces_get_200_response GET /v1/tms/pending-stopper/taskforces(schedd, collector)



    For internal use only (TMS): Retrieves the next taskforce ready to stop at the specified HTCondor location.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **schedd** | **String**| name of the condor schedd | [default to null] |
| **collector** | **String**| DEPRECATED: name of the condor collector -- no longer used/needed | [optional] [default to null] |

### Return type

[**_v1_tms_pending_stopper_taskforces_get_200_response**](../Models/_v1_tms_pending_stopper_taskforces_get_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="POST /v1/tms/statuses/taskforces"></a>
# **POST /v1/tms/statuses/taskforces**
> _v1_tms_statuses_taskforces_post_200_response POST /v1/tms/statuses/taskforces(\_v1\_tms\_statuses\_taskforces\_post\_request)



    For internal use only (TMS): Updates and returns the statuses and errors for the specified taskforces.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **\_v1\_tms\_statuses\_taskforces\_post\_request** | [**_v1_tms_statuses_taskforces_post_request**](../Models/_v1_tms_statuses_taskforces_post_request.md)|  | [optional] |

### Return type

[**_v1_tms_statuses_taskforces_post_200_response**](../Models/_v1_tms_statuses_taskforces_post_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="POST /v1/workflows"></a>
# **POST /v1/workflows**
> _v1_workflows_post_200_response POST /v1/workflows(\_v1\_workflows\_post\_request)



    Creates a new workflow along with its associated task directives and taskforces.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **\_v1\_workflows\_post\_request** | [**_v1_workflows_post_request**](../Models/_v1_workflows_post_request.md)|  | [optional] |

### Return type

[**_v1_workflows_post_200_response**](../Models/_v1_workflows_post_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="POST /v1/workflows/{workflow_id}/actions/abort"></a>
# **POST /v1/workflows/{workflow_id}/actions/abort**
> DeactivatedWorkflowResponseObject POST /v1/workflows/{workflow_id}/actions/abort(workflow\_id)



    Aborts the specified workflow (and marks as &#39;deactivated&#39;), then sends stop commands to the associated taskforces.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **workflow\_id** | **String**| The ID of the workflow object | [default to null] |

### Return type

[**DeactivatedWorkflowResponseObject**](../Models/DeactivatedWorkflowResponseObject.md)

### Authorization


### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="POST /v1/workflows/{workflow_id}/actions/finished"></a>
# **POST /v1/workflows/{workflow_id}/actions/finished**
> DeactivatedWorkflowResponseObject POST /v1/workflows/{workflow_id}/actions/finished(workflow\_id)



    Marks the specified workflow as finished (and &#39;deactivated&#39;), then sends stop commands to the associated taskforces.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **workflow\_id** | **String**| The ID of the workflow object | [default to null] |

### Return type

[**DeactivatedWorkflowResponseObject**](../Models/DeactivatedWorkflowResponseObject.md)

### Authorization


### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="GET /v1/workflows/{workflow_id}"></a>
# **GET /v1/workflows/{workflow_id}**
> WorkflowObject GET /v1/workflows/{workflow_id}(workflow\_id)



    Retrieves the workflow object that matches the specified workflow ID.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **workflow\_id** | **String**| The ID of the workflow object | [default to null] |

### Return type

[**WorkflowObject**](../Models/WorkflowObject.md)

### Authorization


### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

