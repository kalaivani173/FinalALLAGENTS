# Product Note: ReqPay (CHG-670)

## Change Summary
This document outlines the addition of a new XML attribute, `delegate`, to the `Txn` element in the ReqPay API. This change is aimed at enhancing the transaction capabilities within the UPI framework.

## Business Rationale
The addition of the `delegate` attribute is intended to provide flexibility in transaction processing, allowing for better handling of delegated transactions. This change is driven by the need to improve user experience and meet evolving business requirements.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes:
- Update the `Txn` element in the ReqPay API to include the new optional attribute `delegate`.
- The `delegate` attribute must accept values of either "Y" (Yes) or "N" (No).
- Ensure that the attribute is handled correctly in transaction processing logic.

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
- **Effective Date**: [Insert Go-Live Date]
- **Migration Steps**: Ensure that all systems are updated to accommodate the new `delegate` attribute before the effective date.
- **Rollout Considerations**: Monitor transaction processing for any issues related to the new attribute post-implementation.