# Product Note: ReqPay (CHG-644)

## Change Summary
This document outlines the addition of a new XML attribute, `BINDINGMODE`, to the `Device` element within the `ReqPay` API. This change is aimed at enhancing the device identification process during payment requests.

## Business Rationale
The addition of the `BINDINGMODE` attribute is driven by the need to improve the flexibility and accuracy of device identification in payment transactions. By allowing for multiple binding modes, this change supports a broader range of device types and communication methods, thereby enhancing user experience and operational efficiency.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes to comply with the updated `ReqPay` API:
- **New Attribute**: The `Device` element must now include the `BINDINGMODE` attribute.
  - **Attribute Name**: `BINDINGMODE`
  - **Data Type**: `xs:string`
  - **Mandatory**: Yes
  - **Allowed Values**: 
    - `MMS`
    - `SMS`

## Schema Changes
The following changes have been made to the XSD schema:
- **Element**: `Device`
  - **New Attribute**: `BINDINGMODE`
    - **Type**: `BINDINGMODEType`
    - **Use**: Required
- **New Simple Type**: `BINDINGMODEType`
  - **Allowed Values**:
    - `MMS`
    - `SMS`

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Effective Date**: [Insert effective date here]
- **Migration Steps**: Ensure that all systems are updated to include the new `BINDINGMODE` attribute in the `Device` element before the effective date.
- **Rollout Considerations**: Testing should be conducted to ensure compatibility with existing systems and to validate the correct implementation of the new attribute.