# Product Note: ReqPay (CHG-570)

## Change Summary
This document outlines the addition of a new XML attribute, `BINDINGMODE`, to the `Device` element within the `ReqPay` API. This change aims to enhance the data structure by allowing the specification of the binding mode used during the transaction process.

## Business Rationale
The addition of the `BINDINGMODE` attribute is driven by the need to provide more granular control over transaction handling methods. By specifying whether the transaction is conducted via SMS or RSMS, the system can better accommodate varying operational requirements and improve overall transaction reliability.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes to comply with the updated `ReqPay` API:
- Add the `BINDINGMODE` attribute to the `Device` element located at the path `ReqPay.Payer.Device`.
- The `BINDINGMODE` attribute is of type `xs:string`, is optional, and can take the following values:
  - `SMS`
  - `RSMS`

## Schema Changes
The following changes have been made to the XSD schema:
- **Element Added**: `BINDINGMODE` attribute to the `Device` element.
  - **Location**: `ReqPay.Payer.Device`
  - **Type**: `xs:string`
  - **Mandatory**: No
  - **Allowed Values**: `SMS`, `RSMS`

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Effective Date**: [Insert effective date here]
- **Migration Steps**: Ensure that the updated schema is integrated into your systems prior to the effective date.
- **Rollout Considerations**: Testing should be conducted to verify that the new attribute is correctly handled in all relevant transaction scenarios.