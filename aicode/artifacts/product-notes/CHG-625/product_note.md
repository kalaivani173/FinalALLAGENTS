# Product Note: ReqPay (CHG-625)

## Change Summary
This document outlines the addition of a new XML attribute, `BINDINGMODE`, to the `Device` element within the `ReqPay` API. This change is aimed at enhancing the data structure to accommodate new binding modes for device communication.

## Business Rationale
The addition of the `BINDINGMODE` attribute is driven by the need to support multiple communication methods for device interactions. This change aligns with evolving product requirements and enhances the flexibility of the UPI ecosystem.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes:
- Update the `ReqPay` API to include the new `BINDINGMODE` attribute within the `Device` element.
- Ensure that the `BINDINGMODE` attribute is marked as mandatory and accepts only the following values: `SMS`, `RSMS`, and `SMV`.

## Schema Changes
The following changes have been made to the XSD schema:
- **Element Added**: `BINDINGMODE` attribute to the `Device` element.
  - **Data Type**: `xs:string`
  - **Mandatory**: Yes
  - **Allowed Values**: `SMS`, `RSMS`, `SMV`

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Effective Date**: [Insert effective date here]
- **Migration Steps**: Ensure that all systems interacting with the `ReqPay` API are updated to handle the new `BINDINGMODE` attribute.
- **Rollout Considerations**: Monitor for any integration issues post-implementation and provide support for any queries related to the new attribute.