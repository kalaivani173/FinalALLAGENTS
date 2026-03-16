# Product Note: ReqPay (CHG-612)

## Change Summary
This document outlines the addition of a new XML attribute, `BINDINGMODE`, to the `Device` element within the `ReqPay` API. This change aims to enhance the flexibility of the API by allowing the specification of the binding mode used during the transaction process.

## Business Rationale
The addition of the `BINDINGMODE` attribute is driven by the need to support multiple communication methods for transaction requests, specifically "SMS" and "RSMS". This change aligns with evolving product requirements and enhances the user experience by providing more options for transaction initiation.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes in their systems:
- Update the `ReqPay` API to include the new `BINDINGMODE` attribute within the `Device` element.
- The `BINDINGMODE` attribute is optional and can take one of the following values: "SMS" or "RSMS".
- Ensure that the API can handle requests with and without the `BINDINGMODE` attribute.

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
- **Rollout Considerations**: Monitor the implementation for any issues related to the new attribute and provide support as needed during the transition period.