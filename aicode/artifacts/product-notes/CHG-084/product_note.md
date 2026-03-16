# Product Note: ReqPay (CHG-084)

## Change Summary
This document outlines the addition of a new XML attribute, `BINDINGMODE`, to the `Device` element within the `ReqPay` API. This change aims to enhance the flexibility of device communication methods by allowing the specification of the binding mode used for transactions.

## Business Rationale
The addition of the `BINDINGMODE` attribute is driven by the need to support multiple communication methods (SMS and MMS) for transaction notifications. This change aligns with evolving customer preferences and regulatory requirements for improved transaction communication.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes in their systems:
- Update the `Device` element in the `ReqPay` API payload to include the new optional attribute `BINDINGMODE`.
- The `BINDINGMODE` attribute must accept one of the following values: `SMS` or `MMS`.
- Ensure that the attribute is not mandatory, allowing for backward compatibility with existing implementations.

## Schema Changes
The following changes have been made to the XSD schema:
- **Element Added**: `BINDINGMODE` attribute to the `Device` element.
- **Data Type**: `xs:string`.
- **Allowed Values**: `SMS`, `MMS`.
- **Mandatory**: No.

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Effective Date**: [Insert effective date here]
- **Migration Steps**: Ensure that all systems are updated to accommodate the new `BINDINGMODE` attribute before the effective date.
- **Rollout Considerations**: Monitor for any issues related to the new attribute during the initial rollout phase and provide support as needed.