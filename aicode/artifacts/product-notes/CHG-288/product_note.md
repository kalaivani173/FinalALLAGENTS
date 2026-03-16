# Product Note: ReqPay (CHG-288)

## Change Summary
This document outlines the addition of a new XML attribute, `Bindingmode`, to the `Device` element within the `ReqPay` API. This change is aimed at enhancing the device identification process during payment requests.

## Business Rationale
The addition of the `Bindingmode` attribute is driven by the need to improve the accuracy and reliability of device identification in payment transactions. This change aligns with industry standards and enhances the overall user experience by providing clearer device context.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes:
- Add the `Bindingmode` attribute to the `Device` element in the `ReqPay` API payload.
- The `Bindingmode` attribute is mandatory and must be of type `xs:string` with allowed values of `SMS` or `RSMS`.

## Schema Changes
The following changes have been made to the XSD schema:
- **Element Added**: `Bindingmode` attribute to the `Device` element.
  - **Type**: `xs:string`
  - **Mandatory**: Yes
  - **Allowed Values**: `SMS`, `RSMS`

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Effective Date**: [Insert effective date here]
- **Migration Steps**: Ensure that all systems are updated to include the new `Bindingmode` attribute in the `Device` element before the effective date.
- **Rollout Considerations**: Monitor for any issues related to device identification post-implementation and provide support as needed.