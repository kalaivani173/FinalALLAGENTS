# Product Note: ReqPay (CHG-229)

## Change Summary
This document outlines the addition of a new XML attribute, `delegate`, to the `Txn` element in the ReqPay API. This change is intended to enhance the transaction metadata by allowing the specification of delegation status.

## Business Rationale
The addition of the `delegate` attribute is driven by the need for improved transaction tracking and management. By enabling the specification of whether a transaction is delegated, stakeholders can better manage and monitor transaction flows, thereby enhancing operational efficiency.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes to accommodate the new `delegate` attribute:
- Update the `Txn` element in the ReqPay API to include the `delegate` attribute.
- The `delegate` attribute is of type `xs:string`, is optional, and can take the values "Y" (Yes) or "N" (No).

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
- **Migration Steps**: Ensure that all systems interacting with the ReqPay API are updated to handle the new `delegate` attribute.
- **Rollout Considerations**: Monitor transaction processing for any issues related to the new attribute post-implementation.