# Product Note: ReqPay (CHG-939)

## Change Summary
This document outlines the addition of a new XML attribute, `delegate`, to the `Txn` element in the ReqPay API. This change is aimed at enhancing the transaction capabilities within the UPI framework.

## Business Rationale
The addition of the `delegate` field is intended to provide flexibility in transaction processing, allowing for better handling of delegated transactions. This change is driven by the need to accommodate evolving business requirements and improve user experience.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes:
- Add the `delegate` attribute to the `Txn` element in the ReqPay API.
- The `delegate` attribute is of type `xs:string`, is optional, and can take the values "Y" or "N".

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
- Ensure that all systems are updated to accommodate the new `delegate` attribute before the go-live date.
- Monitor transaction processing closely post-implementation to identify any issues related to the new attribute.