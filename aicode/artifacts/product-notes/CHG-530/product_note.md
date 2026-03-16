# Product Note: ReqPay (CHG-530)

## Change Summary
This document outlines the addition of a new XML attribute, `BINDINGMODE`, to the existing `ReqPay` API under the `Device` element. This change aims to enhance the API's capability by allowing the specification of the binding mode used during the transaction process.

## Business Rationale
The addition of the `BINDINGMODE` attribute is driven by the need to provide more granular control over the transaction process. By allowing the specification of binding modes such as "SMS" and "RSMS", the API can better accommodate varying transaction requirements and improve overall user experience.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes to accommodate the new attribute:
- Update the `ReqPay` API to include the `BINDINGMODE` attribute within the `Device` element.
- The `BINDINGMODE` attribute is of type `xs:string`, is optional, and can take the following values:
  - `SMS`
  - `RSMS`

## Schema Changes
The following changes have been made to the XSD schema:
- **Element**: `Device`
  - **New Attribute**: `BINDINGMODE`
    - **Type**: `xs:string`
    - **Mandatory**: No
    - **Allowed Values**: `SMS`, `RSMS`

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Go-Live Date**: [Insert Go-Live Date]
- **Migration Steps**: Ensure that all systems interacting with the `ReqPay` API are updated to handle the new `BINDINGMODE` attribute.
- **Rollout Considerations**: Monitor the implementation for any issues related to the new attribute and provide support as needed during the transition period.