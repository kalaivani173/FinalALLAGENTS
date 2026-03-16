# Product Note: ReqPayDelegate (CHG-668)

## Change Summary
This document outlines the addition of a new XML attribute, `delegate`, to the `Txn` element in the `ReqPayDelegate` API. This change is intended to enhance the transaction request capabilities by allowing the specification of delegation in payment requests.

## Business Rationale
The addition of the `delegate` attribute is driven by the need to provide more flexibility in transaction processing. By allowing the specification of delegation, this change supports various business scenarios where transactions may need to be processed on behalf of another party, thereby improving the overall user experience and operational efficiency.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes in their systems:
- Update the `ReqPayDelegate` API to include the new `delegate` attribute in the `Txn` element.
- The `delegate` attribute is of type `xs:string`, is optional, and can take the values "Y" (Yes) or "N" (No).

### Field Additions
- **XML Path**: `ReqPayDelegate.Txn`
- **Element Name**: `Txn`
- **Attribute Name**: `delegate`
- **Data Type**: `xs:string`
- **Mandatory**: No
- **Allowed Values**: 
  - "Y"
  - "N"

## Schema Changes
The following changes have been made to the XSD schema:
- Added the optional attribute `delegate` to the `Txn` element:
  ```xml
  <xs:attribute name="delegate" type="xs:string" use="optional"/>
  ```

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Go-Live Date**: [Insert Go-Live Date]
- **Migration Steps**: Ensure that all systems are updated to accommodate the new `delegate` attribute before the go-live date.
- **Rollout Considerations**: Monitor the implementation for any issues related to the new attribute and provide support as needed during the transition period.