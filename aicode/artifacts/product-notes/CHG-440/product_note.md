# Product Note: ReqPay (CHG-440)

## Change Summary
This document outlines the addition of a new XML attribute, `BINDINGMODE`, to the `Device` element within the `ReqPay` API. This change aims to enhance the flexibility of device communication methods by allowing the specification of either SMS or MMS as the binding mode.

## Business Rationale
The addition of the `BINDINGMODE` attribute is driven by the need to accommodate varying communication preferences among users. By enabling the selection of SMS or MMS, the API can better serve diverse use cases and improve user experience.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes:
- Update the `Device` element in the `ReqPay` API to include the new optional attribute `BINDINGMODE`.
- Ensure that the `BINDINGMODE` attribute can accept the values "SMS" or "MMS".

## Schema Changes
The following changes have been made to the XSD schema:
- **Element**: `Device`
  - **New Attribute**: `BINDINGMODE`
    - **Type**: `xs:string`
    - **Mandatory**: No
    - **Allowed Values**: "SMS", "MMS"

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Change ID**: CHG-440
- **Effective Date**: [Insert Go-Live Date]
- **Migration Steps**: Ensure that all systems interacting with the `ReqPay` API are updated to handle the new `BINDINGMODE` attribute prior to the effective date. Testing should be conducted to confirm compatibility with existing implementations.