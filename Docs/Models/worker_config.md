# worker_config
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **do\_transfer\_worker\_stdouterr** | **Boolean** | Indicates whether to transfer back the workers&#39; stdout and stderr (accessible on the AP). | [default to null] |
| **max\_worker\_runtime** | **Integer** | The maximum runtime for a worker. Adjust this to optimize performance (e.g., to terminate slow CPUs). | [default to null] |
| **n\_cores** | **Integer** | The number of cores to request per HTCondor worker. | [default to null] |
| **priority** | **Integer** | The priority level for the HTCondor submission. | [default to null] |
| **worker\_disk** | [**worker_config_worker_disk**](worker_config_worker_disk.md) |  | [default to null] |
| **worker\_memory** | [**worker_config_worker_memory**](worker_config_worker_memory.md) |  | [default to null] |
| **condor\_requirements** | **String** | The &#39;requirements&#39; string given to the HTCondor submission. | [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

