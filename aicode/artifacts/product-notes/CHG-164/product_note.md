# Product Note: ReqPay (CHG-164)

## Change Summary
This document outlines the addition of a new XML attribute, `BINDINGMODE`, to the `Device` element within the `ReqPay` API. This change is aimed at enhancing the device identification process during transaction requests.

## Business Rationale
The addition of the `BINDINGMODE` attribute is driven by the need to improve transaction security and device identification. By specifying the binding mode, the system can better manage and authenticate the devices used in payment transactions, aligning with industry standards for secure payment processing.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes in their systems:
- Add the `BINDINGMODE` attribute to the `Device` element in the `ReqPay` API payload.
- Ensure that the `BINDINGMODE` attribute is of type `xs:string`, is mandatory, and can only accept the values `SMS` or `RSMS`.

## Schema Changes
The following changes have been made to the XSD schema:
- **Element Added**: `BINDINGMODE` attribute to the `Device` element.
  - **Type**: `xs:string`
  - **Mandatory**: Yes
  - **Allowed Values**: `SMS`, `RSMS`

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Effective Date**: [Insert effective date here]
- **Migration Steps**: Ensure that all systems are updated to include the new `BINDINGMODE` attribute before the effective date.
- **Rollout Considerations**: Monitor transaction requests for compliance with the new attribute requirements post-implementation.