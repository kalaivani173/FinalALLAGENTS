# Product Note: ReqPay (CHG-911)

## Change Summary
This document outlines the addition of a new XML attribute, `BINDINGMODE`, to the `Device` element within the `ReqPay` API. This change aims to enhance the flexibility of device binding methods used in payment requests.

## Business Rationale
The introduction of the `BINDINGMODE` attribute is driven by the need to support multiple device binding methods, specifically `SMS` and `RSMS`. This change aligns with evolving market demands and enhances the user experience by providing more options for transaction notifications.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes in their systems:
- Update the `ReqPay` API to include the new `BINDINGMODE` attribute within the `Device` element.
- The `BINDINGMODE` attribute is optional and can take the values `SMS` or `RSMS`.
- Ensure that the XML payloads sent to and received from the API conform to the updated schema.

### Field Additions
- **XML Path**: `ReqPay.Payer.Device`
- **Element Name**: `Device`
- **Attribute Name**: `BINDINGMODE`
- **Data Type**: `xs:string`
- **Mandatory**: No
- **Allowed Values**: 
  - `SMS`
  - `RSMS`

## Schema Changes
The following changes have been made to the XSD schema:
- Added a new attribute `BINDINGMODE` to the `Device` element within the `Payer` structure.
- Defined `BINDINGMODE` as an optional attribute with a simple type restriction allowing values `SMS` and `RSMS`.

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Effective Date**: [Insert effective date here]
- **Migration Steps**: Ensure that all systems are updated to handle the new `BINDINGMODE` attribute before the effective date.
- **Rollout Considerations**: Monitor transaction flows post-implementation to ensure that the new binding methods are functioning as expected.