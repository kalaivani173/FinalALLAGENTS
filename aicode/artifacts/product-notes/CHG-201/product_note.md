# Product Note: ReqPay (CHG-201)

## Change Summary
This document outlines the addition of a new XML attribute, `BINDINGMODE`, to the `Device` element within the `ReqPay` API. This change aims to enhance the flexibility of device binding modes used in payment requests.

## Business Rationale
The addition of the `BINDINGMODE` attribute is driven by the need to accommodate different modes of communication for payment requests, specifically allowing for SMS and RSMS options. This change aligns with evolving product requirements and enhances user experience by providing more options for transaction notifications.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes in their systems:
- Update the `Device` element in the `ReqPay` API to include the new optional attribute `BINDINGMODE`.
- The `BINDINGMODE` attribute must accept the following values:
  - `SMS`
  - `RSMS`
- Ensure that the attribute is not mandatory, allowing for backward compatibility.

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
- **Go-Live Date**: [Insert Go-Live Date]
- **Migration Steps**: Ensure that all systems are updated to accommodate the new `BINDINGMODE` attribute before the go-live date.
- **Rollout Considerations**: Monitor the implementation for any issues related to the new attribute and ensure that all stakeholders are informed of the changes.