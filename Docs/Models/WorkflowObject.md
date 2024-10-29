# WorkflowObject

## Properties

| Name                                | Type           | Description                                                                                                       | Notes                        |
|-------------------------------------|----------------|-------------------------------------------------------------------------------------------------------------------|------------------------------|
| **workflow\_id**                    | **String**     | A unique identifier automatically generated for this workflow.                                                    | [optional] [default to null] |
| **timestamp**                       | **BigDecimal** | The epoch time when this workflow was created.                                                                    | [optional] [default to null] |
| **priority**                        | **Integer**    | The workflow&#39;s priority level relative to other workflows.                                                    | [optional] [default to null] |
| **mq\_activated\_ts**               | **BigDecimal** | The epoch time when message queues were created for this workflow. If null, the queues have not yet been created. | [optional] [default to null] |
| **\_mq\_activation\_retry\_at\_ts** | **BigDecimal** | For internal use only: The epoch time to retry requesting message queues from MQS.                                | [optional] [default to null] |
| **deactivated**                     | **Boolean**    | Indicates whether the workflow has been deactivated.                                                              | [optional] [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
