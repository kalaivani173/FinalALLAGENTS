# Product Note: ReqPay (CHG-106)

## Change Summary
This document outlines the addition of a new XML attribute, `delegate`, to the `Txn` element in the ReqPay API. This change is intended to enhance transaction logging capabilities.

## Business Rationale
The addition of the `delegate` attribute is aimed at improving transaction tracking and management. This change is driven by the need for better data granularity in transaction logs, which can assist in regulatory compliance and enhance product functionality.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes:
- Add the `delegate` attribute to the `Txn` element in the XML payload.
- The `delegate` attribute is of type `xs:string`, is optional, and can take the values "Y" or "N".

## Schema Changes
The following changes have been made to the XSD schema:
- **Element Added**: 
  - `delegate` attribute to the `Txn` element.
    - **Type**: `xs:string`
    - **Mandatory**: No
    - **Allowed Values**: "Y", "N"

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- Ensure that all systems are updated to accommodate the new `delegate` attribute before the go-live date.
- Monitor transaction logs post-implementation to verify the correct usage of the new attribute.