# WorkflowObject
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **workflow\_id** | **String** | the unique ID for this workflow object (auto-created) | [optional] [default to null] |
| **timestamp** | **BigDecimal** | the time (epoch) when this workflow object was created | [optional] [default to null] |
| **priority** | **Integer** | the priority of the workflow in relation to other workflows | [optional] [default to null] |
| **mq\_activated\_ts** | **BigDecimal** |  | [optional] [default to null] |
| **\_mq\_activation\_retry\_at\_ts** | **BigDecimal** | internal use only: when to retry requesting message queues from MQS | [optional] [default to null] |
| **aborted** | **Boolean** | whether the workflow has been aborted | [optional] [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

