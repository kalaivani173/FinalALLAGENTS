# Product Note: ReqPay (CHG-766)

## Change Summary
This document outlines the addition of a new XML attribute, `delegate`, to the `Txn` element in the ReqPay API. This change is identified by Change ID CHG-766 and is intended to enhance the functionality of the API.

## Business Rationale
The addition of the `delegate` attribute is aimed at providing more flexibility in transaction processing. This change is driven by the need to accommodate varying transaction scenarios and improve the overall user experience.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes to comply with this update:
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
- **Go-Live Date**: [Insert Go-Live Date]
- **Migration Steps**: Ensure that the updated schema is integrated into your systems prior to the go-live date.
- **Rollout Considerations**: Monitor the implementation for any issues related to the new attribute during the initial rollout phase.