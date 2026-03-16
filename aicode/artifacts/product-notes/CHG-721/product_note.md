# Product Note: ReqPay (CHG-721)

## Change Summary
This document outlines the addition of a new XML attribute, `delegate`, to the `Txn` element in the ReqPay API. This change is intended to enhance the transaction data structure by allowing the inclusion of delegate information.

## Business Rationale
The addition of the `delegate` attribute is driven by the need for improved transaction tracking and management. By enabling the specification of a delegate, the system can better accommodate scenarios where transactions are processed on behalf of another party, thereby enhancing operational efficiency and compliance.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes in their systems:
- Update the ReqPay API to include the new `delegate` attribute in the `Txn` element.
- The `delegate` attribute is of type `xs:string`, is optional, and does not have any predefined allowed values.

## Schema Changes
The following changes have been made to the XSD schema:
- **Element**: `Txn`
  - **Attribute Added**: `delegate`
    - **Type**: `xs:string`
    - **Mandatory**: No

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Go-Live Date**: [Insert Go-Live Date]
- **Migration Steps**: Ensure that all systems are updated to accommodate the new `delegate` attribute before the go-live date.
- **Rollout Considerations**: Monitor transaction processing closely post-implementation to ensure that the new attribute is being utilized correctly.