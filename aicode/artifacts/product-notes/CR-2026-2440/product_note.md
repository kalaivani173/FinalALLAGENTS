# Product Note: ReqPay (CR-2026-2440)

## Change Summary
This document outlines the addition of a new XML attribute, "Remarks," to the ReqPay API under the Txn element. This change is intended to enhance the transaction details by allowing additional contextual information to be included.

## Business Rationale
The addition of the "Remarks" attribute is aimed at improving transaction clarity and providing users with the ability to include supplementary information that may be relevant for transaction processing or auditing purposes. This change is driven by the need for enhanced data granularity in transaction records.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes in their systems:
- Update the ReqPay API to include the new optional attribute "Remarks" within the Txn element.
- Ensure that the "Remarks" attribute can accept a string value, with the allowed value being "any."
- The attribute is not mandatory, allowing flexibility in transaction submissions.

## Schema Changes
The following changes have been made to the XSD schema:
- **New Attribute Added**: 
  - **Name**: Remarks
  - **Type**: RemarksType (xs:string)
  - **Usage**: Optional
  - **Location**: Txn element

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Effective Date**: [Insert effective date here]
- **Migration Steps**: Ensure that all systems are updated to accommodate the new "Remarks" attribute before the effective date.
- **Rollout Considerations**: Monitor transaction submissions for compliance with the new schema and provide support for any issues arising from the implementation of this change.