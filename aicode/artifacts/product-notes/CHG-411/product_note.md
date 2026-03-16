# Product Note: ReqPay (CHG-411)

## Change Summary
This document outlines the addition of a new XML attribute, `BINDINGMODE`, to the `Device` element within the `ReqPay` API. This change is intended to enhance the flexibility of device binding methods used in payment requests.

## Business Rationale
The addition of the `BINDINGMODE` attribute is driven by the need to support multiple device binding methods, specifically `MMS` and `SMS`. This change aligns with evolving market requirements and enhances the user experience by providing more options for transaction initiation.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes in their systems:
- Add the `BINDINGMODE` attribute to the `Device` element in the `ReqPay` API payload.
- The `BINDINGMODE` attribute is of type `xs:string`, is optional, and can take the values `MMS` or `SMS`.

## Schema Changes
The following changes have been made to the XSD schema:
- **Element**: `Device`
  - **New Attribute**: `BINDINGMODE`
    - **Type**: `xs:string`
    - **Mandatory**: No
    - **Allowed Values**: `MMS`, `SMS`

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Effective Date**: [Insert Go-Live Date]
- **Migration Steps**: Ensure that all systems are updated to accommodate the new `BINDINGMODE` attribute before the effective date.
- **Rollout Considerations**: Monitor the implementation for any issues related to the new attribute and provide support as needed during the transition period.