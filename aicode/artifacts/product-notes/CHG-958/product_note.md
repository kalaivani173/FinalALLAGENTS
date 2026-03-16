# Product Note: ReqPay (CHG-958)

## Change Summary
This document outlines the addition of a new XML attribute, `BINDINGMODE`, to the `Device` element within the `ReqPay` API. This change is intended to enhance the functionality of the API by allowing the specification of the binding mode used during transactions.

## Business Rationale
The introduction of the `BINDINGMODE` attribute is driven by the need to provide greater flexibility in transaction handling. By allowing the specification of binding modes such as "SMS" and "RSMS", the API can better accommodate varying transaction requirements and improve user experience.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes to accommodate the new attribute:
- **XML Path**: `ReqPay.Payer.Device`
- **New Attribute**: 
  - **Name**: `BINDINGMODE`
  - **Data Type**: `xs:string`
  - **Mandatory**: No
  - **Allowed Values**: 
    - `SMS`
    - `RSMS`

## Schema Changes
The following changes have been made to the XSD schema:
- Added a new attribute `BINDINGMODE` to the `Device` element within the `Payer` structure. This attribute is of type `BINDINGMODEType`, which restricts its values to "SMS" and "RSMS".

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Change ID**: CHG-958
- **API Name**: ReqPay
- **Effective Date**: [Insert Go-Live Date]
- **Migration Steps**: Ensure that the updated XSD schema is integrated into your systems and that the new attribute is correctly handled in transaction requests. Testing should be conducted to verify the implementation before the go-live date.