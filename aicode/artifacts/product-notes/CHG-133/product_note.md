# Product Note: ReqPay (CHG-133)

## Change Summary
This document outlines the addition of a new XML attribute, `delegate`, to the `Txn` element in the ReqPay API. The attribute is optional and can take on the values "Y" or "N".

## Business Rationale
The addition of the `delegate` attribute is intended to enhance the flexibility of the ReqPay API, allowing for more nuanced transaction handling. This change addresses product needs for improved transaction categorization and management.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes in their systems:
- Add the `delegate` attribute to the `Txn` element in the ReqPay API payload.
- Ensure that the `delegate` attribute is optional and can accept the values "Y" or "N".

## Schema Changes
The following changes have been made to the XSD schema:
- **Element**: `Txn`
  - **Attribute Added**: `delegate`
    - **Type**: `xs:string`
    - **Mandatory**: No
    - **Allowed Values**: "Y", "N"

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Effective Date**: [Insert effective date here]
- **Migration Steps**: Ensure that all systems are updated to accommodate the new `delegate` attribute before the effective date.
- **Rollout Considerations**: Monitor transaction processing for any issues related to the new attribute post-implementation.