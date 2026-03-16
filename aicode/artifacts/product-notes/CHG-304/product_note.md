# Product Note: ReqPay (CHG-304)

## Change Summary
This document outlines the addition of a new XML attribute, `BINDINGMODE`, to the `Device` element within the `ReqPay` API. This change allows for the specification of the input method for SMS and MMS communications.

## Business Rationale
The addition of the `BINDINGMODE` attribute is driven by the need to enhance the flexibility of the `ReqPay` API in handling different communication methods. This change aligns with evolving product requirements and ensures compliance with industry standards for messaging services.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes:
- Add the `BINDINGMODE` attribute to the `Device` element in the `ReqPay` API payload.
- The `BINDINGMODE` attribute is mandatory and must be set to either `MMS` or `SMS`.

## Schema Changes
The following changes have been made to the XSD schema:
- **Element Added**: `BINDINGMODE` attribute to the `Device` element.
  - **Data Type**: `xs:string`
  - **Mandatory**: Yes
  - **Allowed Values**: `MMS`, `SMS`

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Effective Date**: [Insert effective date here]
- **Migration Steps**: Ensure that all systems utilizing the `ReqPay` API are updated to accommodate the new `BINDINGMODE` attribute before the effective date.
- **Rollout Considerations**: Monitor for any issues related to the implementation of the new attribute during the initial rollout phase.