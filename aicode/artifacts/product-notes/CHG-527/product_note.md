# Product Note: ReqPay (CHG-527)

## Change Summary
This document outlines the addition of a new XML attribute, `BINDINGMODE`, to the `Device` element within the `ReqPay` API. This change aims to enhance the flexibility of device binding options for payment requests.

## Business Rationale
The addition of the `BINDINGMODE` attribute is driven by the need to accommodate varying methods of device communication, specifically through SMS and RSMS. This change aligns with evolving market demands and enhances the user experience by providing more options for transaction notifications.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes:
- Update the `Device` element in the `ReqPay` API to include the new optional attribute `BINDINGMODE`.
- The `BINDINGMODE` attribute must accept the following values:
  - `SMS`
  - `RSMS`
- Ensure that the attribute is not mandatory, allowing for backward compatibility with existing implementations.

## Schema Changes
The following changes have been made to the XSD schema:
- **Element Added**: `BINDINGMODE` attribute to the `Device` element.
- **Attribute Details**:
  - **Name**: `BINDINGMODE`
  - **Type**: `xs:string`
  - **Mandatory**: No
  - **Allowed Values**: `SMS`, `RSMS`

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Effective Date**: [Insert effective date here]
- **Migration Steps**: Ensure that all systems are updated to accommodate the new `BINDINGMODE` attribute before the effective date.
- **Rollout Considerations**: Monitor for any issues related to the new attribute during the initial rollout phase and provide support as needed.