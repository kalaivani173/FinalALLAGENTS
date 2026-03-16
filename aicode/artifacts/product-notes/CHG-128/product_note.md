# Product Note: ReqPay (CHG-128)

## Change Summary
This document outlines the addition of a new optional XML attribute, `delegate`, to the `Txn` element in the ReqPay API. This change is aimed at enhancing the flexibility of transaction requests by allowing the specification of delegation status.

## Business Rationale
The addition of the `delegate` field is intended to meet evolving business needs and improve transaction handling capabilities. By allowing the specification of delegation, this change supports better transaction management and aligns with industry best practices.

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
- **Rollout Considerations**: Monitor transaction processing for any issues related to the new attribute post-implementation.