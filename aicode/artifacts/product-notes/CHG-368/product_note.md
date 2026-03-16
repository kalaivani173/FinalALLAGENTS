# Product Note: ReqPay (CHG-368)

## Change Summary
This document outlines the addition of a new XML attribute, `delegate`, to the `Txn` element in the ReqPay API. This change is intended to enhance the transaction data structure by allowing the specification of delegation status.

## Business Rationale
The addition of the `delegate` attribute is aimed at improving transaction handling capabilities within the UPI framework. This change is driven by the need for enhanced transaction metadata, which can facilitate better processing and tracking of transactions, thereby improving overall service quality.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes in their systems:
- Update the `Txn` element in the ReqPay API to include the new optional attribute `delegate`.
- The `delegate` attribute must accept values of either "Y" (Yes) or "N" (No).
- Ensure that the attribute is not mandatory, allowing for backward compatibility with existing implementations.

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
- **Rollout Considerations**: Monitor transaction processing post-implementation to ensure that the new attribute is being utilized correctly and does not disrupt existing workflows.