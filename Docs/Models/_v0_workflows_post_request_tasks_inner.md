# _v0_workflows_post_request_tasks_inner
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **cluster\_locations** | **Set** | The HTCondor pool(s) where the taskforce(s) will run. | [default to null] |
| **task\_image** | **String** | The Docker/Singularity/Apptainer image to run for each event. Apptainer images in directory (sandbox) format will start fastest; other formats will first be converted to this format on each worker CPU. | [default to null] |
| **task\_args** | **String** | The argument string to pass to the task image. | [default to null] |
| **task\_env** | [**Object**](.md) | Environment variables (and values) to set in the task instance. | [optional] [default to null] |
| **init\_image** | **String** | The Docker/Singularity/Apptainer image to run for each event. Apptainer images in directory (sandbox) format will start fastest; other formats will first be converted to this format on each worker CPU. | [optional] [default to null] |
| **init\_args** | **String** | The argument string to pass to the task image. | [optional] [default to null] |
| **init\_env** | [**Object**](.md) | Environment variables (and values) to set in the task instance. | [optional] [default to null] |
| **input\_queue\_aliases** | **Set** | User-defined aliases for input event queues. Globally-unique IDs for the queues will be generated after submission. | [default to null] |
| **output\_queue\_aliases** | **Set** | User-defined aliases for output event queues. Globally-unique IDs for the queues will be generated after submission. | [default to null] |
| **pilot\_config** | [**TaskforceObject_pilot_config**](TaskforceObject_pilot_config.md) |  | [optional] [default to null] |
| **worker\_config** | [**TaskforceObject_worker_config**](TaskforceObject_worker_config.md) |  | [default to null] |
| **n\_workers** | **Integer** | The number of workers in this taskforce&#39;s HTCondor cluster (immutable). | [optional] [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

