# Product Note: ReqPay (CHG-934)

## Change Summary
This document outlines the addition of a new XML attribute, `BINDINGMODE`, to the `Device` element within the `ReqPay` API. This change aims to enhance the flexibility of device binding methods in payment requests.

## Business Rationale
The addition of the `BINDINGMODE` attribute is driven by the need to support multiple communication methods (SMS and MMS) for payment requests. This change aligns with evolving user preferences and regulatory requirements for enhanced communication options in digital payment systems.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes:
- Update the `Device` element in the `ReqPay` API to include the new optional attribute `BINDINGMODE`.
- The `BINDINGMODE` attribute must accept the values "SMS" or "MMS".
- Ensure that the attribute is not mandatory, allowing for backward compatibility with existing implementations.

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
- **Effective Date**: [Insert effective date here]
- **Migration Steps**: Ensure that all systems are updated to accommodate the new `BINDINGMODE` attribute before the effective date.
- **Rollout Considerations**: Monitor for any issues related to the implementation of the new attribute during the initial rollout phase.