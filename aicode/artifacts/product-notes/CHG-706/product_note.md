# Product Note: ReqPay (CHG-706)

## Change Summary
This document outlines the addition of a new XML attribute, `delegate`, to the `Txn` element in the ReqPay API. This change is designed to enhance the functionality of the API by allowing the specification of delegation in transaction requests.

## Business Rationale
The addition of the `delegate` attribute is driven by the need for improved transaction handling and flexibility in payment processing. This change will enable better management of transaction responsibilities, aligning with evolving business requirements and enhancing user experience.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes to accommodate the new `delegate` attribute:
- Update the `Txn` element in the ReqPay API to include the `delegate` attribute.
- The `delegate` attribute is of type `xs:string`, is optional, and can take the values "Y" or "N".

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
- **Migration Steps**: Ensure that all systems interacting with the ReqPay API are updated to handle the new `delegate` attribute.
- **Rollout Considerations**: Monitor transaction processing post-implementation to ensure that the new attribute is functioning as intended and that there are no disruptions in service.