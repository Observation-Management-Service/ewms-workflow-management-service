# pilot_config
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **tag** | **String** | The image tag to use (e.g., &#39;v#.#.#&#39;, &#39;latest&#39;, or a feature branch tag). This field is useful for repeatability. | [default to null] |
| **environment** | [**Map**](pilot_config_environment_value.md) | Environment variables and their corresponding values. | [default to null] |
| **input\_files** | **Set** | Paths to files to make available to the task container. These files must already be accessible on the AP. | [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

