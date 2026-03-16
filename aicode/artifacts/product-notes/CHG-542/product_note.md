# Product Note: ReqPay (CHG-542)

## Change Summary
This document outlines the addition of a new XML attribute, `BINDINGCODE`, to the `Device` element within the `ReqPay` API. This change aims to enhance the data structure by allowing the specification of the binding method used for communication.

## Business Rationale
The addition of the `BINDINGCODE` attribute is driven by the need to provide more granular information regarding the communication method used in transactions. This change supports better tracking and reporting capabilities, aligning with industry standards and improving user experience.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes in their systems:
- Add the `BINDINGCODE` attribute to the `Device` element in the `ReqPay` API payload.
- The `BINDINGCODE` attribute is of type `xs:string`, is optional, and can take the following values:
  - `SMS`
  - `MMS`

## Schema Changes
The following changes have been made to the XSD schema:
- **Element Added**: `BINDINGCODE` attribute to the `Device` element.
  - **Type**: `xs:string`
  - **Mandatory**: No
  - **Allowed Values**: `SMS`, `MMS`

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Effective Date**: [Insert effective date here]
- **Migration Steps**: Ensure that all systems are updated to accommodate the new `BINDINGCODE` attribute before the effective date.
- **Rollout Considerations**: Monitor the implementation for any issues related to the new attribute and provide support as needed during the transition period.