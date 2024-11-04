# _v0_tms_pending_starter_taskforces_get_200_response
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **taskforce\_uuid** | **String** | A unique identifier automatically generated for this taskforce. | [optional] [default to null] |
| **task\_id** | **String** | The identifier of the associated task directive object (N taskforces : 1 task directive). | [optional] [default to null] |
| **workflow\_id** | **String** | The identifier of the overarching workflow object (N*M taskforces : M task directives : 1 workflow). | [optional] [default to null] |
| **timestamp** | **BigDecimal** | The epoch time when this taskforce was created. | [optional] [default to null] |
| **priority** | **Integer** | The priority level relative to other taskforces (usually, this value is inherited from the parent workflow object). | [optional] [default to null] |
| **collector** | **String** | The address of the HTCondor collector. | [optional] [default to null] |
| **schedd** | **String** | The address of the HTCondor schedd. | [optional] [default to null] |
| **n\_workers** | [**TaskforceObject_n_workers**](TaskforceObject_n_workers.md) |  | [optional] [default to null] |
| **pilot\_config** | [**TaskforceObject_pilot_config**](TaskforceObject_pilot_config.md) |  | [optional] [default to null] |
| **worker\_config** | [**TaskforceObject_worker_config**](TaskforceObject_worker_config.md) |  | [optional] [default to null] |
| **cluster\_id** | [**TaskforceObject_cluster_id**](TaskforceObject_cluster_id.md) |  | [optional] [default to null] |
| **submit\_dict** | [**Map**](TaskforceObject_submit_dict_value.md) | The actual HTCondor submit class ad. | [optional] [default to null] |
| **job\_event\_log\_fpath** | **String** | The file path on the HTCondor AP containing job event logs. | [optional] [default to null] |
| **phase** | **String** | The current phase of the taskforce within the workflow&#39;s lifetime. Not all taskforces will enter every phase. | [optional] [default to null] |
| **phase\_change\_log** | [**List**](AnyType.md) | A record of all attempted phase changes, including both successful and unsuccessful ones. | [optional] [default to null] |
| **compound\_statuses** | [**Map**](map.md) | Aggregated status of the workers, represented as a nested dictionary mapping HTCondor states to EWMS pilot states and their counts. | [optional] [default to null] |
| **top\_task\_errors** | **Map** | The most common errors encountered by workers, paired with their occurrence counts. | [optional] [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

