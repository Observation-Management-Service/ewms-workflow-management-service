# DefaultApi

All URIs are relative to *http://localhost*

| Method                                                                                                                       | HTTP request                                                | Description |
|------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------|-------------|
| [**rootGet**](DefaultApi.md#rootGet)                                                                                         | **GET** /                                                   |             |
| [**schemaOpenapiGet**](DefaultApi.md#schemaOpenapiGet)                                                                       | **GET** /schema/openapi                                     |             |
| [**taskDirectiveTaskIdGet**](DefaultApi.md#taskDirectiveTaskIdGet)                                                           | **GET** /task-directives/{task_id}                          |             |
| [**taskDirectivesFindPost**](DefaultApi.md#taskDirectivesFindPost)                                                           | **POST** /task-directives/find                              |             |
| [**taskforceTaskforceUuidGet**](DefaultApi.md#taskforceTaskforceUuidGet)                                                     | **GET** /taskforces/{taskforce_uuid}                        |             |
| [**taskforceTmsActionCondorSubmitTaskforceUuidPost**](DefaultApi.md#taskforceTmsActionCondorSubmitTaskforceUuidPost)         | **POST** /taskforces/{taskforce_uuid}/tms/condor-submit     |             |
| [**taskforceTmsActionPendingStarterGet**](DefaultApi.md#taskforceTmsActionPendingStarterGet)                                 | **GET** /tms/pending-starter/taskforces                     |             |
| [**taskforceTmsActionPendingStopperGet**](DefaultApi.md#taskforceTmsActionPendingStopperGet)                                 | **GET** /tms/pending-stopper/taskforces                     |             |
| [**taskforceTmsActionPendingStopperTaskforceUuidDelete**](DefaultApi.md#taskforceTmsActionPendingStopperTaskforceUuidDelete) | **DELETE** /tms/pending-stopper/taskforces/{taskforce_uuid} |             |
| [**taskforceTmsCondorCompleteTaskforceUuidPost**](DefaultApi.md#taskforceTmsCondorCompleteTaskforceUuidPost)                 | **POST** /tms/condor-complete/taskforces/{taskforce_uuid}   |             |
| [**taskforcesFindPost**](DefaultApi.md#taskforcesFindPost)                                                                   | **POST** /taskforces/find                                   |             |
| [**taskforcesTmsStatusPost**](DefaultApi.md#taskforcesTmsStatusPost)                                                         | **POST** /tms/taskforces/statuses                           |             |
| [**workflowsFindPost**](DefaultApi.md#workflowsFindPost)                                                                     | **POST** /workflows/find                                    |             |
| [**workflowsPost**](DefaultApi.md#workflowsPost)                                                                             | **POST** /workflows                                         |             |
| [**workflowsWorkflowIdDelete**](DefaultApi.md#workflowsWorkflowIdDelete)                                                     | **DELETE** /workflows/{workflow_id}                         |             |
| [**workflowsWorkflowIdGet**](DefaultApi.md#workflowsWorkflowIdGet)                                                           | **GET** /workflows/{workflow_id}                            |             |

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

<a name="taskDirectiveTaskIdGet"></a>

# **taskDirectiveTaskIdGet**

> TaskDirectiveObject taskDirectiveTaskIdGet(task\_id)

### Parameters

| Name         | Type       | Description                  | Notes             |
|--------------|------------|------------------------------|-------------------|
| **task\_id** | **String** | the id of the task directive | [default to null] |

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

| Name           | Type                                      | Description | Notes      |
|----------------|-------------------------------------------|-------------|------------|
| **FindObject** | [**FindObject**](../Models/FindObject.md) |             | [optional] |

### Return type

[**_task_directives_find_post_200_response**](../Models/_task_directives_find_post_200_response.md)

### Authorization

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="taskforceTaskforceUuidGet"></a>

# **taskforceTaskforceUuidGet**

> TaskforceObject taskforceTaskforceUuidGet(taskforce\_uuid)

### Parameters

| Name                | Type       | Description                     | Notes             |
|---------------------|------------|---------------------------------|-------------------|
| **taskforce\_uuid** | **String** | the taskforce object&#39;s uuid | [default to null] |

### Return type

[**TaskforceObject**](../Models/TaskforceObject.md)

### Authorization

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="taskforceTmsActionCondorSubmitTaskforceUuidPost"></a>

# **taskforceTmsActionCondorSubmitTaskforceUuidPost**

> TaskforceUUIDObject taskforceTmsActionCondorSubmitTaskforceUuidPost(taskforce\_uuid, TaskforceObject)

### Parameters

| Name                | Type                                                | Description                     | Notes             |
|---------------------|-----------------------------------------------------|---------------------------------|-------------------|
| **taskforce\_uuid** | **String**                                          | the taskforce object&#39;s uuid | [default to null] |
| **TaskforceObject** | [**TaskforceObject**](../Models/TaskforceObject.md) |                                 | [optional]        |

### Return type

[**TaskforceUUIDObject**](../Models/TaskforceUUIDObject.md)

### Authorization

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="taskforceTmsActionPendingStarterGet"></a>

# **taskforceTmsActionPendingStarterGet**

> _taskforce_tms_action_pending_starter_get_200_response taskforceTmsActionPendingStarterGet(collector, schedd)

### Parameters

| Name          | Type       | Description                  | Notes             |
|---------------|------------|------------------------------|-------------------|
| **collector** | **String** | name of the condor collector | [default to null] |
| **schedd**    | **String** | name of the condor schedd    | [default to null] |

### Return type

[**_taskforce_tms_action_pending_starter_get_200_response
**](../Models/_taskforce_tms_action_pending_starter_get_200_response.md)

### Authorization

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="taskforceTmsActionPendingStopperGet"></a>

# **taskforceTmsActionPendingStopperGet**

> _taskforce_tms_action_pending_starter_get_200_response taskforceTmsActionPendingStopperGet(collector, schedd)

### Parameters

| Name          | Type       | Description                  | Notes             |
|---------------|------------|------------------------------|-------------------|
| **collector** | **String** | name of the condor collector | [default to null] |
| **schedd**    | **String** | name of the condor schedd    | [default to null] |

### Return type

[**_taskforce_tms_action_pending_starter_get_200_response
**](../Models/_taskforce_tms_action_pending_starter_get_200_response.md)

### Authorization

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="taskforceTmsActionPendingStopperTaskforceUuidDelete"></a>

# **taskforceTmsActionPendingStopperTaskforceUuidDelete**

> TaskforceUUIDObject taskforceTmsActionPendingStopperTaskforceUuidDelete(taskforce\_uuid)

### Parameters

| Name                | Type       | Description                     | Notes             |
|---------------------|------------|---------------------------------|-------------------|
| **taskforce\_uuid** | **String** | the taskforce object&#39;s uuid | [default to null] |

### Return type

[**TaskforceUUIDObject**](../Models/TaskforceUUIDObject.md)

### Authorization

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="taskforceTmsCondorCompleteTaskforceUuidPost"></a>

# **taskforceTmsCondorCompleteTaskforceUuidPost**

> TaskforceUUIDObject taskforceTmsCondorCompleteTaskforceUuidPost(taskforce\_uuid,
> \_taskforce\_tms\_condor\_complete\_\_taskforce\_uuid\_\_post\_request)

### Parameters

| Name                                                                       | Type                                                                                                                                          | Description                     | Notes             |
|----------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------|-------------------|
| **taskforce\_uuid**                                                        | **String**                                                                                                                                    | the taskforce object&#39;s uuid | [default to null] |
| **\_taskforce\_tms\_condor\_complete\_\_taskforce\_uuid\_\_post\_request** | [**_taskforce_tms_condor_complete__taskforce_uuid__post_request**](../Models/_taskforce_tms_condor_complete__taskforce_uuid__post_request.md) |                                 | [optional]        |

### Return type

[**TaskforceUUIDObject**](../Models/TaskforceUUIDObject.md)

### Authorization

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="taskforcesFindPost"></a>

# **taskforcesFindPost**

> _taskforces_find_post_200_response taskforcesFindPost(FindObject)

### Parameters

| Name           | Type                                      | Description | Notes      |
|----------------|-------------------------------------------|-------------|------------|
| **FindObject** | [**FindObject**](../Models/FindObject.md) |             | [optional] |

### Return type

[**_taskforces_find_post_200_response**](../Models/_taskforces_find_post_200_response.md)

### Authorization

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="taskforcesTmsStatusPost"></a>

# **taskforcesTmsStatusPost**

> _taskforces_tms_status_post_200_response taskforcesTmsStatusPost(\_taskforces\_tms\_status\_post\_request)

### Parameters

| Name                                         | Type                                                                                        | Description | Notes      |
|----------------------------------------------|---------------------------------------------------------------------------------------------|-------------|------------|
| **\_taskforces\_tms\_status\_post\_request** | [**_taskforces_tms_status_post_request**](../Models/_taskforces_tms_status_post_request.md) |             | [optional] |

### Return type

[**_taskforces_tms_status_post_200_response**](../Models/_taskforces_tms_status_post_200_response.md)

### Authorization

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="workflowsFindPost"></a>

# **workflowsFindPost**

> _workflows_find_post_200_response workflowsFindPost(FindObject)

### Parameters

| Name           | Type                                      | Description | Notes      |
|----------------|-------------------------------------------|-------------|------------|
| **FindObject** | [**FindObject**](../Models/FindObject.md) |             | [optional] |

### Return type

[**_workflows_find_post_200_response**](../Models/_workflows_find_post_200_response.md)

### Authorization

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="workflowsPost"></a>

# **workflowsPost**

> _workflows_post_200_response workflowsPost(\_workflows\_post\_request)

### Parameters

| Name                           | Type                                                                | Description | Notes      |
|--------------------------------|---------------------------------------------------------------------|-------------|------------|
| **\_workflows\_post\_request** | [**_workflows_post_request**](../Models/_workflows_post_request.md) |             | [optional] |

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

| Name             | Type       | Description                   | Notes             |
|------------------|------------|-------------------------------|-------------------|
| **workflow\_id** | **String** | the id of the workflow object | [default to null] |

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

| Name             | Type       | Description                   | Notes             |
|------------------|------------|-------------------------------|-------------------|
| **workflow\_id** | **String** | the id of the workflow object | [default to null] |

### Return type

[**WorkflowObject**](../Models/WorkflowObject.md)

### Authorization

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json
