# Product Note: ReqPay (CHG-243)

## Change Summary
This document outlines the addition of a new XML attribute, `delegate`, to the `Txn` element in the ReqPay API. This change is part of ongoing efforts to enhance the functionality and flexibility of the UPI payment processing system.

## Business Rationale
The addition of the `delegate` attribute is intended to support enhanced transaction management and tracking capabilities within the ReqPay API. This change is driven by the need for improved transaction handling and reporting, which aligns with evolving business requirements and user feedback.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes to accommodate the new attribute:
- Add the `delegate` attribute to the `Txn` element in the XML payload.
- The `delegate` attribute is of type `xs:string`, is optional, and does not have any predefined allowed values.

## Schema Changes
The following changes have been made to the XSD schema:
- **Element Modified**: `Txn`
  - **New Attribute Added**: 
    - `delegate` (type: `xs:string`, mandatory: false)

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Change ID**: CHG-243
- **Effective Date**: [Insert Go-Live Date]
- **Migration Steps**: Ensure that all systems interacting with the ReqPay API are updated to handle the new `delegate` attribute in the `Txn` element.
- **Rollout Considerations**: Monitor transaction processing for any issues related to the new attribute post-implementation.