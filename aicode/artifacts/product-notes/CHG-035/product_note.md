# Product Note: ReqPay (CHG-035)

## Change Summary
This document outlines the addition of a new XML attribute, `BINDINGMODE`, to the `Device` element within the `ReqPay` API. This change is aimed at enhancing the device identification process during transaction requests.

## Business Rationale
The addition of the `BINDINGMODE` attribute is driven by the need to improve transaction security and device identification. By specifying the binding mode, which can be either `SMS` or `DMS`, the system can better manage and authenticate transaction requests, aligning with industry best practices.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes:
- Update the `ReqPay` API to include the new `BINDINGMODE` attribute within the `Device` element.
- Ensure that the `BINDINGMODE` attribute is mandatory and accepts only the values `SMS` or `DMS`.
- Validate that the attribute is included in the XML payload for all relevant transaction requests.

## Schema Changes
The following changes have been made to the XSD schema:
- **Element Added**: `BINDINGMODE` attribute to the `Device` element.
  - **Data Type**: `xs:string`
  - **Mandatory**: Yes
  - **Allowed Values**: `SMS`, `DMS`

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Effective Date**: [Insert effective date here]
- **Migration Steps**: Ensure that all systems are updated to accommodate the new `BINDINGMODE` attribute before the effective date.
- **Rollout Considerations**: Monitor transaction requests for compliance with the new attribute requirements post-implementation.