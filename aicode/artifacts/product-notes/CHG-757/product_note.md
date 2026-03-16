# Product Note: ReqPay (CHG-757)

## Change Summary
This document outlines the addition of a new XML attribute, `BINDINGMODE`, to the `Device` element within the `ReqPay` API. This change is aimed at enhancing the functionality of the API by allowing the specification of the binding mode used during payment requests.

## Business Rationale
The introduction of the `BINDINGMODE` attribute is driven by the need to provide greater flexibility and control over the payment request process. By allowing the specification of binding modes such as "SMS" and "RSMS", the API can better accommodate varying operational requirements and improve user experience.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes to comply with the updated `ReqPay` API:
- Add the `BINDINGMODE` attribute to the `Device` element within the `Payer` section of the API payload.
- Ensure that the `BINDINGMODE` attribute is of type `xs:string`, is mandatory, and can only accept the values "SMS" or "RSMS".

## Schema Changes
The following changes have been made to the XSD schema:
- **Element Added**: `BINDINGMODE` attribute to the `Device` element.
  - **Type**: `xs:string`
  - **Mandatory**: Yes
  - **Allowed Values**: "SMS", "RSMS"

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Effective Date**: [Insert effective date here]
- **Migration Steps**: PSPs and banks should update their systems to include the new `BINDINGMODE` attribute in the `Device` element of the `ReqPay` API payload.
- **Rollout Considerations**: Ensure thorough testing of the updated API to validate the correct implementation of the new attribute and its impact on existing functionalities.