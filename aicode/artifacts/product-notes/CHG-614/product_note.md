# Product Note: ReqPay (CHG-614)

## Change Summary
This document outlines the addition of a new XML attribute, `BINDINGMODE`, to the `Device` element within the `ReqPay` API. This change is aimed at enhancing the device identification process during payment requests.

## Business Rationale
The addition of the `BINDINGMODE` attribute is driven by the need to improve the clarity and specificity of device communication methods used in payment transactions. By allowing for explicit identification of the binding mode, this change supports better transaction tracking and compliance with evolving regulatory requirements.

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
- **Effective Date**: [Insert Go-Live Date]
- **Migration Steps**: Ensure that all systems are updated to include the new `BINDINGMODE` attribute before the effective date.
- **Rollout Considerations**: Monitor transaction logs for any discrepancies related to device identification post-implementation.