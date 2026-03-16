# Product Note: ReqPay (CHG-134)

## Change Summary
This document outlines the addition of a new XML attribute, `delegate`, to the `Txn` element in the ReqPay API. This change is intended to enhance the transaction request capabilities by allowing the specification of delegation in transaction processing.

## Business Rationale
The addition of the `delegate` attribute is driven by the need for improved transaction management and flexibility in handling requests. This change will enable better tracking and processing of transactions that may require delegation, aligning with evolving business requirements and enhancing user experience.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes in their systems:
- Update the `Txn` element in the ReqPay API to include the new optional attribute `delegate`.
- The `delegate` attribute must accept values of either "Y" (Yes) or "N" (No).
- Ensure that the attribute is handled correctly in transaction processing logic, as it is not mandatory.

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