# Product Note: ReqPay (CHG-018)

## Change Summary
This document outlines the addition of a new XML attribute, `BINDINGMODE`, to the `Device` element within the `ReqPay` API. This change aims to enhance the flexibility of device identification methods used in payment requests.

## Business Rationale
The introduction of the `BINDINGMODE` attribute is driven by the need to support multiple device communication methods, specifically MMS and SMS. This change aligns with evolving market demands and enhances the user experience by allowing for more versatile transaction processing.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes:
- Update the `Device` element in the `ReqPay` API to include the new optional attribute `BINDINGMODE`.
- The `BINDINGMODE` attribute must accept the following values: `MMS` and `SMS`.
- Ensure that the attribute is not mandatory, allowing for backward compatibility with existing implementations.

## Schema Changes
The following changes have been made to the XSD schema:
- **Element Added**: `BINDINGMODE` attribute to the `Device` element.
  - **Data Type**: `xs:string`
  - **Mandatory**: No
  - **Allowed Values**: `MMS`, `SMS`

## Sample Payloads
No sample payloads were provided for this change.

## Go-Live Notes
- **Effective Date**: [Insert effective date here]
- **Migration Steps**: Ensure that all systems are updated to accommodate the new `BINDINGMODE` attribute before the effective date.
- **Rollout Considerations**: Monitor for any issues during the transition period and provide support for any queries related to the new attribute.