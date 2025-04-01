# DefaultApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [_details_](DefaultApi.md#post-v0querytask-directives) | **POST** /v0/query/task-directives |  |
| [_details_](DefaultApi.md#post-v0querytaskforces) | **POST** /v0/query/taskforces |  |
| [_details_](DefaultApi.md#post-v0queryworkflows) | **POST** /v0/query/workflows |  |
| [_details_](DefaultApi.md#get-v0root) | **GET** /v0/root |  |
| [_details_](DefaultApi.md#get-v0schemaopenapi) | **GET** /v0/schema/openapi |  |
| [_details_](DefaultApi.md#post-v0task-directivestask_idactionsadd-workers) | **POST** /v0/task-directives/{task_id}/actions/add-workers |  |
| [_details_](DefaultApi.md#get-v0task-directivestask_id) | **GET** /v0/task-directives/{task_id} |  |
| [_details_](DefaultApi.md#get-v0taskforcestaskforce_uuid) | **GET** /v0/taskforces/{taskforce_uuid} |  |
| [_details_](DefaultApi.md#post-v0tmscondor-completetaskforcestaskforce_uuid) | **POST** /v0/tms/condor-complete/taskforces/{taskforce_uuid} |  |
| [_details_](DefaultApi.md#post-v0tmscondor-rmtaskforcestaskforce_uuidfailed) | **POST** /v0/tms/condor-rm/taskforces/{taskforce_uuid}/failed |  |
| [_details_](DefaultApi.md#post-v0tmscondor-rmtaskforcestaskforce_uuid) | **POST** /v0/tms/condor-rm/taskforces/{taskforce_uuid} |  |
| [_details_](DefaultApi.md#post-v0tmscondor-submittaskforcestaskforce_uuidfailed) | **POST** /v0/tms/condor-submit/taskforces/{taskforce_uuid}/failed |  |
| [_details_](DefaultApi.md#post-v0tmscondor-submittaskforcestaskforce_uuid) | **POST** /v0/tms/condor-submit/taskforces/{taskforce_uuid} |  |
| [_details_](DefaultApi.md#get-v0tmspending-startertaskforces) | **GET** /v0/tms/pending-starter/taskforces |  |
| [_details_](DefaultApi.md#get-v0tmspending-stoppertaskforces) | **GET** /v0/tms/pending-stopper/taskforces |  |
| [_details_](DefaultApi.md#post-v0tmsstatusestaskforces) | **POST** /v0/tms/statuses/taskforces |  |
| [_details_](DefaultApi.md#post-v0workflows) | **POST** /v0/workflows |  |
| [_details_](DefaultApi.md#post-v0workflowsworkflow_idactionsabort) | **POST** /v0/workflows/{workflow_id}/actions/abort |  |
| [_details_](DefaultApi.md#post-v0workflowsworkflow_idactionsfinished) | **POST** /v0/workflows/{workflow_id}/actions/finished |  |
| [_details_](DefaultApi.md#get-v0workflowsworkflow_id) | **GET** /v0/workflows/{workflow_id} |  |


<a name="POST /v0/query/task-directives"></a>
# **POST /v0/query/task-directives**
> _v0_query_task_directives_post_200_response POST /v0/query/task-directives(FindObject)



    Queries and returns a list of task directive objects based on the provided criteria.

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



    Queries and returns a list of taskforce objects based on the provided criteria.

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



    Queries and returns a list of workflow objects based on the provided criteria.

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

<a name="GET /v0/root"></a>
# **GET /v0/root**
> GET /v0/root()



    Returns an empty response.

### Parameters
This endpoint does not need any parameter.

### Return type

null (empty response body)

### Authorization


### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="GET /v0/schema/openapi"></a>
# **GET /v0/schema/openapi**
> Map GET /v0/schema/openapi()



    Returns the OpenAPI schema.

### Parameters
This endpoint does not need any parameter.

### Return type

[**Map**](../Models/AnyType.md)

### Authorization


### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="POST /v0/task-directives/{task_id}/actions/add-workers"></a>
# **POST /v0/task-directives/{task_id}/actions/add-workers**
> TaskforceObject POST /v0/task-directives/{task_id}/actions/add-workers(task\_id, \_v0\_task\_directives\_\_task\_id\_\_actions\_add\_workers\_post\_request)



    Creates a new taskforce (and associated workers) for an existing task directive.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **task\_id** | **String**| The ID of the task directive to which the taskforce (and workers) will be added. | [default to null] |
| **\_v0\_task\_directives\_\_task\_id\_\_actions\_add\_workers\_post\_request** | [**_v0_task_directives__task_id__actions_add_workers_post_request**](../Models/_v0_task_directives__task_id__actions_add_workers_post_request.md)|  | [optional] |

### Return type

[**TaskforceObject**](../Models/TaskforceObject.md)

### Authorization


### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="GET /v0/task-directives/{task_id}"></a>
# **GET /v0/task-directives/{task_id}**
> TaskDirectiveObject GET /v0/task-directives/{task_id}(task\_id)



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

<a name="GET /v0/taskforces/{taskforce_uuid}"></a>
# **GET /v0/taskforces/{taskforce_uuid}**
> TaskforceObject GET /v0/taskforces/{taskforce_uuid}(taskforce\_uuid)



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

<a name="POST /v0/tms/condor-complete/taskforces/{taskforce_uuid}"></a>
# **POST /v0/tms/condor-complete/taskforces/{taskforce_uuid}**
> _v0_tms_condor_complete_taskforces__taskforce_uuid__post_200_response POST /v0/tms/condor-complete/taskforces/{taskforce_uuid}(taskforce\_uuid, \_v0\_tms\_condor\_complete\_taskforces\_\_taskforce\_uuid\_\_post\_request)



    For internal use only (TMS): Updates the specified taskforce with the completion timestamp of the HTCondor cluster.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **taskforce\_uuid** | **String**| uuid of the taskforce | [default to null] |
| **\_v0\_tms\_condor\_complete\_taskforces\_\_taskforce\_uuid\_\_post\_request** | [**_v0_tms_condor_complete_taskforces__taskforce_uuid__post_request**](../Models/_v0_tms_condor_complete_taskforces__taskforce_uuid__post_request.md)|  | [optional] |

### Return type

[**_v0_tms_condor_complete_taskforces__taskforce_uuid__post_200_response**](../Models/_v0_tms_condor_complete_taskforces__taskforce_uuid__post_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="POST /v0/tms/condor-rm/taskforces/{taskforce_uuid}/failed"></a>
# **POST /v0/tms/condor-rm/taskforces/{taskforce_uuid}/failed**
> _v0_tms_condor_complete_taskforces__taskforce_uuid__post_200_response POST /v0/tms/condor-rm/taskforces/{taskforce_uuid}/failed(taskforce\_uuid, \_v0\_tms\_condor\_rm\_taskforces\_\_taskforce\_uuid\_\_failed\_post\_request)



    For internal use only (TMS): Communicates that a taskforce failed to be removed on HTCondor.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **taskforce\_uuid** | **String**| uuid of the taskforce | [default to null] |
| **\_v0\_tms\_condor\_rm\_taskforces\_\_taskforce\_uuid\_\_failed\_post\_request** | [**_v0_tms_condor_rm_taskforces__taskforce_uuid__failed_post_request**](../Models/_v0_tms_condor_rm_taskforces__taskforce_uuid__failed_post_request.md)|  | [optional] |

### Return type

[**_v0_tms_condor_complete_taskforces__taskforce_uuid__post_200_response**](../Models/_v0_tms_condor_complete_taskforces__taskforce_uuid__post_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="POST /v0/tms/condor-rm/taskforces/{taskforce_uuid}"></a>
# **POST /v0/tms/condor-rm/taskforces/{taskforce_uuid}**
> _v0_tms_condor_complete_taskforces__taskforce_uuid__post_200_response POST /v0/tms/condor-rm/taskforces/{taskforce_uuid}(taskforce\_uuid)



    For internal use only (TMS): Confirms that a taskforce has been removed on HTCondor.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **taskforce\_uuid** | **String**| uuid of the taskforce | [default to null] |

### Return type

[**_v0_tms_condor_complete_taskforces__taskforce_uuid__post_200_response**](../Models/_v0_tms_condor_complete_taskforces__taskforce_uuid__post_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="POST /v0/tms/condor-submit/taskforces/{taskforce_uuid}/failed"></a>
# **POST /v0/tms/condor-submit/taskforces/{taskforce_uuid}/failed**
> _v0_tms_condor_complete_taskforces__taskforce_uuid__post_200_response POST /v0/tms/condor-submit/taskforces/{taskforce_uuid}/failed(taskforce\_uuid, \_v0\_tms\_condor\_submit\_taskforces\_\_taskforce\_uuid\_\_failed\_post\_request)



    For internal use only (TMS): Communicates that a taskforce failed to be submitted to HTCondor for execution.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **taskforce\_uuid** | **String**| uuid of the taskforce | [default to null] |
| **\_v0\_tms\_condor\_submit\_taskforces\_\_taskforce\_uuid\_\_failed\_post\_request** | [**_v0_tms_condor_submit_taskforces__taskforce_uuid__failed_post_request**](../Models/_v0_tms_condor_submit_taskforces__taskforce_uuid__failed_post_request.md)|  | [optional] |

### Return type

[**_v0_tms_condor_complete_taskforces__taskforce_uuid__post_200_response**](../Models/_v0_tms_condor_complete_taskforces__taskforce_uuid__post_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="POST /v0/tms/condor-submit/taskforces/{taskforce_uuid}"></a>
# **POST /v0/tms/condor-submit/taskforces/{taskforce_uuid}**
> _v0_tms_condor_complete_taskforces__taskforce_uuid__post_200_response POST /v0/tms/condor-submit/taskforces/{taskforce_uuid}(taskforce\_uuid, TaskforceObject)



    For internal use only (TMS): Confirms that a taskforce has been submitted to HTCondor for execution.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **taskforce\_uuid** | **String**| uuid of the taskforce | [default to null] |
| **TaskforceObject** | [**TaskforceObject**](../Models/TaskforceObject.md)|  | [optional] |

### Return type

[**_v0_tms_condor_complete_taskforces__taskforce_uuid__post_200_response**](../Models/_v0_tms_condor_complete_taskforces__taskforce_uuid__post_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="GET /v0/tms/pending-starter/taskforces"></a>
# **GET /v0/tms/pending-starter/taskforces**
> _v0_tms_pending_starter_taskforces_get_200_response GET /v0/tms/pending-starter/taskforces(collector, schedd)



    For internal use only (TMS): Retrieves the next taskforce ready to start at the specified HTCondor location.

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
> _v0_tms_pending_stopper_taskforces_get_200_response GET /v0/tms/pending-stopper/taskforces(collector, schedd)



    For internal use only (TMS): Retrieves the next taskforce ready to stop at the specified HTCondor location.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **collector** | **String**| name of the condor collector | [default to null] |
| **schedd** | **String**| name of the condor schedd | [default to null] |

### Return type

[**_v0_tms_pending_stopper_taskforces_get_200_response**](../Models/_v0_tms_pending_stopper_taskforces_get_200_response.md)

### Authorization


### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="POST /v0/tms/statuses/taskforces"></a>
# **POST /v0/tms/statuses/taskforces**
> _v0_tms_statuses_taskforces_post_200_response POST /v0/tms/statuses/taskforces(\_v0\_tms\_statuses\_taskforces\_post\_request)



    For internal use only (TMS): Updates and returns the statuses and errors for the specified taskforces.

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



    Creates a new workflow along with its associated task directives and taskforces.

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

<a name="POST /v0/workflows/{workflow_id}/actions/abort"></a>
# **POST /v0/workflows/{workflow_id}/actions/abort**
> DeactivatedWorkflowResponseObject POST /v0/workflows/{workflow_id}/actions/abort(workflow\_id)



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

<a name="POST /v0/workflows/{workflow_id}/actions/finished"></a>
# **POST /v0/workflows/{workflow_id}/actions/finished**
> DeactivatedWorkflowResponseObject POST /v0/workflows/{workflow_id}/actions/finished(workflow\_id)



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

<a name="GET /v0/workflows/{workflow_id}"></a>
# **GET /v0/workflows/{workflow_id}**
> WorkflowObject GET /v0/workflows/{workflow_id}(workflow\_id)



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

