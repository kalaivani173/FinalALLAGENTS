# Product Note: ReqPay (CHG-459)

## Change Summary
This document outlines the addition of a new XML attribute, `delegate`, to the `Txn` element in the ReqPay API. This change is intended to enhance the transaction data structure by allowing the specification of delegation status.

## Business Rationale
The addition of the `delegate` attribute is driven by the need for improved transaction handling and reporting. By enabling the specification of delegation, this change supports better tracking and management of transactions, aligning with evolving business requirements and regulatory standards.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes in their systems:
- Update the `Txn` element in the ReqPay API to include the new optional attribute `delegate`.
- The `delegate` attribute must accept values of either "Y" (Yes) or "N" (No).
- Ensure that the attribute is handled correctly in both request and response payloads.

## Schema Changes
The following changes have been made to the XSD schema:
- **Element**: `Txn`
  - **New Attribute**: `delegate`
    - **Type**: `xs:string`
    - **Mandatory**: No
    - **Allowed Values**: "Y", "N"

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Effective Date**: [Insert effective date here]
- **Migration Steps**: Ensure that all systems are updated to accommodate the new `delegate` attribute before the effective date.
- **Rollout Considerations**: Monitor transaction processing for any issues related to the new attribute post-implementation.