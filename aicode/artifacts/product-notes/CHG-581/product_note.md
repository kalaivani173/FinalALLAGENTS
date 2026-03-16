# Product Note: ReqPay (CHG-581)

## Change Summary
This document outlines the addition of a new XML attribute, `BINDINGMODE`, to the `Device` element within the `ReqPay` API. This change is aimed at enhancing the device identification process during payment requests.

## Business Rationale
The addition of the `BINDINGMODE` attribute is driven by the need to improve the clarity and specificity of device communication methods in payment transactions. By allowing the specification of binding modes such as "SMS" and "DMS", the change aligns with evolving regulatory requirements and enhances the overall user experience.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes in their systems:
- Update the `Device` element in the `ReqPay` API to include the new mandatory attribute `BINDINGMODE`.
- Ensure that the `BINDINGMODE` attribute accepts only the allowed values: "SMS" and "DMS".

## Schema Changes
The following changes have been made to the XSD schema:
- **Element Added**: `BINDINGMODE` attribute to the `Device` element.
  - **Type**: `xs:string`
  - **Mandatory**: Yes
  - **Allowed Values**: "SMS", "DMS"

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Effective Date**: [Insert Go-Live Date]
- **Migration Steps**: Ensure that all systems are updated to accommodate the new `BINDINGMODE` attribute before the effective date.
- **Rollout Considerations**: Monitor the implementation for any issues related to the new attribute and provide support as needed during the transition period.