# TaskDirectiveObject
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **task\_id** | **String** | A unique identifier automatically generated for this task. | [optional] [default to null] |
| **workflow\_id** | **String** | The identifier of the overarching workflow object (M task directives : 1 workflow). | [optional] [default to null] |
| **cluster\_locations** | **Set** | The HTCondor pool(s) where the taskforce(s) will run. | [optional] [default to null] |
| **task\_image** | **String** | The Docker/Singularity/Apptainer image to run for each event. Apptainer images in directory (sandbox) format will start fastest; other formats will first be converted to this format on each worker CPU. | [optional] [default to null] |
| **task\_args** | **String** | The argument string to pass to the task image. | [optional] [default to null] |
| **task\_env** | [**Object**](.md) | Environment variables (and values) to set in the task instance. | [optional] [default to null] |
| **init\_image** | **String** | The Docker/Singularity/Apptainer image for the init container. See &#39;task_image&#39; for caveats/optimizations regarding the image format. | [optional] [default to null] |
| **init\_args** | **String** | The argument string to pass to the init container. | [optional] [default to null] |
| **init\_env** | [**Object**](.md) | Environment variables (and values) to set in the init container. | [optional] [default to null] |
| **timestamp** | **BigDecimal** | The epoch time when this task was created. | [optional] [default to null] |
| **input\_queues** | **Set** | The message queue(s) that this task will use for event input. | [optional] [default to null] |
| **output\_queues** | **Set** | The message queue(s) that this task will use for event output. | [optional] [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

