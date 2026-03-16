# Product Note: ReqPay (CHG-965)

## Change Summary
This document outlines the addition of a new XML attribute, `BINDINGMODE`, to the `Device` element in the `ReqPay` API. This change allows for the specification of the device binding mode, with allowed values of "SMS" and "SMV".

## Business Rationale
The introduction of the `BINDINGMODE` attribute is aimed at enhancing the flexibility and security of transactions processed through the UPI system. By allowing the specification of device binding modes, the system can better accommodate varying transaction environments and regulatory requirements.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes:
- Update the `Device` element in the `ReqPay` API to include the new optional attribute `BINDINGMODE`.
- Ensure that the `BINDINGMODE` attribute can accept the values "SMS" or "SMV".
- The attribute is not mandatory, but if included, it must conform to the specified allowed values.

## Schema Changes
The following changes have been made to the XSD schema:
- **Element Modified**: `Device`
  - **New Attribute Added**: `BINDINGMODE`
    - **Type**: `xs:string`
    - **Allowed Values**: "SMS", "SMV"
    - **Mandatory**: No

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Effective Date**: [Insert Go-Live Date]
- **Migration Steps**: Ensure that all systems are updated to accommodate the new `BINDINGMODE` attribute before the effective date.
- **Rollout Considerations**: Monitor transactions for compliance with the new attribute and ensure that any existing integrations are tested for compatibility.