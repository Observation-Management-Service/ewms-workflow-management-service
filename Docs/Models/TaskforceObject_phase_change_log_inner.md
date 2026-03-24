# TaskforceObject_phase_change_log_inner
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **target\_phase** | **String** | The phase that the system was attempting to transition to. | [default to null] |
| **timestamp** | **BigDecimal** | The epoch timestamp when this phase change attempt was recorded in the system. | [default to null] |
| **was\_successful** | **Boolean** | Indicates whether the phase change was completed successfully, i.e. did it actually change? | [default to null] |
| **source\_event\_time** | **BigDecimal** | The epoch timestamp of the external event that led to this phase change attempt. | [default to null] |
| **source\_entity** | **String** | The entity (person, system, or process) responsible for the external event that triggered this phase change attempt. | [default to null] |
| **context** | **String** | The circumstances or background information about the phase change attempt. | [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

