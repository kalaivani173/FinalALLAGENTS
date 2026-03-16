# Product Note: ReqPay (CHG-759)

## Change Summary
This document outlines the addition of a new XML attribute, `BINDINGMODE`, to the `Device` element in the ReqPay API. This change aims to enhance the functionality of the API by allowing the specification of the binding mode used in transactions.

## Business Rationale
The addition of the `BINDINGMODE` attribute is driven by the need to provide more granular control over transaction processing methods. By allowing values such as "SMS" and "RSMS", the API can better accommodate varying transaction requirements and improve user experience.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes in their systems:
- Update the XML schema to include the new `BINDINGMODE` attribute within the `Device` element.
- Ensure that the `BINDINGMODE` attribute is optional and can accept the values "SMS" or "RSMS".

## Schema Changes
The following changes have been made to the XSD schema:
- **Element Added**: `BINDINGMODE` attribute to the `Device` element.
  - **Data Type**: `xs:string`
  - **Mandatory**: No
  - **Allowed Values**: "SMS", "RSMS"

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Go-Live Date**: [Insert Go-Live Date]
- **Migration Steps**: Ensure that all systems are updated to accommodate the new `BINDINGMODE` attribute before the go-live date.
- **Rollout Considerations**: Monitor transaction processing post-implementation to ensure that the new attribute is functioning as intended.