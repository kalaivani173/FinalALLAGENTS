# Product Note: ReqPay (CHG-521)

## Change Summary
This document outlines the addition of a new XML attribute named `delegate` to the `Txn` element in the ReqPay API. This change is intended to enhance the functionality of the API by allowing the specification of delegation in transaction requests.

## Business Rationale
The addition of the `delegate` attribute is driven by the need to provide more flexibility in transaction processing. This change allows for better handling of transactions that may require delegation, thereby improving the overall user experience and meeting evolving business requirements.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes in their systems:
- Update the `Txn` element in the ReqPay API to include the new optional attribute `delegate`.
- The `delegate` attribute must accept values of either "y" (yes) or "n" (no).
- Ensure that the attribute is handled correctly in transaction processing logic.

## Schema Changes
The following changes have been made to the XSD schema:
- **Element**: `Txn`
  - **New Attribute**: `delegate`
    - **Type**: `xs:string`
    - **Mandatory**: No
    - **Allowed Values**: "y", "n"

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Effective Date**: [Insert effective date here]
- **Migration Steps**: Ensure that all systems are updated to accommodate the new `delegate` attribute before the effective date.
- **Rollout Considerations**: Monitor transaction processing for any issues related to the new attribute post-implementation.