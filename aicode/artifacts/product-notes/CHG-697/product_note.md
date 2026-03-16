# Product Note: ReqPay (CHG-697)

## Change Summary
This document outlines the addition of a new XML attribute, `BINDINGMODE`, to the `Device` element within the `ReqPay` API. This change aims to enhance the flexibility of device binding modes in payment requests.

## Business Rationale
The addition of the `BINDINGMODE` attribute is driven by the need to support multiple device communication methods, specifically `MMS` and `SMS`. This change aligns with evolving market demands and enhances the user experience by providing more options for transaction notifications.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes to accommodate the new attribute:
- Update the `Device` element in the `ReqPay` API payload to include the optional `BINDINGMODE` attribute.
- The `BINDINGMODE` attribute must accept the following values:
  - `MMS`
  - `SMS`
- Ensure that the attribute is not mandatory, allowing for flexibility in implementation.

## Schema Changes
The following changes have been made to the XSD schema:
- **Element Added**: `BINDINGMODE` attribute to the `Device` element.
  - **Data Type**: `xs:string`
  - **Mandatory**: No
  - **Allowed Values**: `MMS`, `SMS`

## Sample Payloads
No sample payloads were provided for this change.

## Go-Live Notes
- **Effective Date**: [Insert effective date here]
- **Migration Steps**: Ensure that all systems are updated to handle the new `BINDINGMODE` attribute before the effective date.
- **Rollout Considerations**: Monitor the implementation for any issues related to the new attribute and provide support as needed during the transition period.