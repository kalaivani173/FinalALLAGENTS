# Product Note: ReqPay (CHG-550)

## Change Summary
This document outlines the addition of a new XML attribute, `Device.BINDINGMODE`, to the `Payer` element in the ReqPay API. This change is intended to enhance the data model by allowing the specification of the binding mode used during the transaction.

## Business Rationale
The addition of the `Device.BINDINGMODE` attribute is driven by the need to provide more granular information regarding the device's binding mode during transactions. This enhancement will support better tracking and reporting capabilities, aligning with industry standards and improving user experience.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes in their systems:
- Add the `Device.BINDINGMODE` attribute to the `Payer` element in the ReqPay API payload.
- The attribute is of type `xs:string`, is optional, and can take the following values:
  - `SMS`
  - `RSMS`

## Schema Changes
The following changes have been made to the XSD schema:
- **Element Added**: `Device.BINDINGMODE` as an optional attribute under the `Payer` element.
- **Data Type**: `xs:string`
- **Allowed Values**: 
  - `SMS`
  - `RSMS`

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Effective Date**: [Insert effective date here]
- **Migration Steps**: Ensure that all systems are updated to accommodate the new attribute before the effective date.
- **Rollout Considerations**: Monitor the implementation for any issues related to the new attribute and provide support as needed during the transition period.