# Product Note: ReqPay (CHG-651)

## Change Summary
This document outlines the addition of a new XML attribute, `BINDINGMODE`, to the `Device` element within the `ReqPay` API. This change aims to enhance the functionality of the API by allowing the specification of the binding mode used during the transaction process.

## Business Rationale
The addition of the `BINDINGMODE` attribute is driven by the need to provide more flexibility in transaction handling. By allowing the specification of binding modes such as `SMS` and `RSMS`, the API can better accommodate varying transaction requirements and improve user experience.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes in their systems:
- Update the `ReqPay` API to include the new `BINDINGMODE` attribute within the `Device` element.
- Ensure that the `BINDINGMODE` attribute is optional and can accept the values `SMS` or `RSMS`.

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
- A new attribute `BINDINGMODE` has been added to the `Device` element within the `Payer` structure.
- The `BINDINGMODE` attribute is defined as an optional attribute of type `BINDINGMODEType`, which restricts its values to `SMS` and `RSMS`.

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Effective Date**: [Insert effective date here]
- **Migration Steps**: Ensure that all systems are updated to accommodate the new `BINDINGMODE` attribute before the effective date.
- **Rollout Considerations**: Monitor the implementation for any issues related to the new attribute and provide support as needed during the transition period.