# Product Note: ReqPay (CHG-691)

## Change Summary
This document outlines the addition of a new XML attribute, `BINDINGMODE`, to the `Device` element within the `ReqPay` API. This change is aimed at enhancing the functionality of the API by allowing the specification of the binding mode used for communication.

## Business Rationale
The addition of the `BINDINGMODE` attribute is driven by the need to standardize communication methods between systems. By allowing values such as "SMS" and "MMS", the change facilitates better integration and ensures compliance with evolving communication standards in the payment processing ecosystem.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes:
- Update the `Device` element in the `ReqPay` API to include the new mandatory attribute `BINDINGMODE`.
- Ensure that the `BINDINGMODE` attribute accepts only the allowed values: "SMS" and "MMS".

## Schema Changes
The following changes have been made to the XSD schema:
- **Element Added**: `BINDINGMODE` attribute to the `Device` element.
  - **Data Type**: `xs:string`
  - **Mandatory**: Yes
  - **Allowed Values**: "SMS", "MMS"

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Effective Date**: [Insert Go-Live Date]
- **Migration Steps**: Ensure that all systems using the `ReqPay` API are updated to accommodate the new `BINDINGMODE` attribute before the effective date.
- **Rollout Considerations**: Monitor integration testing closely to ensure that the new attribute is correctly implemented and that systems can handle the specified binding modes.