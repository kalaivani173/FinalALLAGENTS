# Product Note: ReqPay (CHG-003)

## Change Summary
This document outlines the addition of a new XML attribute, `BINDINGMODE`, to the `Device` element within the `ReqPay` API. This change aims to enhance the flexibility of device binding options for payment requests.

## Business Rationale
The introduction of the `BINDINGMODE` attribute is driven by the need to accommodate varying methods of device communication, specifically through SMS and RSMS. This change aligns with evolving market demands and enhances the user experience by providing more options for transaction notifications.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes:
- Add the `BINDINGMODE` attribute to the `Device` element in the `ReqPay` API payload.
- The `BINDINGMODE` attribute is optional and can take the following values:
  - `SMS`
  - `RSMS`

## Schema Changes
The following changes have been made to the XSD schema:
- **Element**: `Device`
  - **New Attribute**: `BINDINGMODE`
    - **Type**: `xs:string`
    - **Mandatory**: No
    - **Allowed Values**: `SMS`, `RSMS`

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Effective Date**: [Insert effective date here]
- **Migration Steps**: Ensure that the updated schema is integrated into your systems prior to the effective date.
- **Rollout Considerations**: Monitor the implementation for any issues related to the new attribute and ensure that all relevant teams are trained on the changes.