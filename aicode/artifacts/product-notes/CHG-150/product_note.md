# Product Note: ReqPay (CHG-150)

## Change Summary
This document outlines the addition of a new XML attribute, `BINDINGMODE`, to the `Device` element within the `ReqPay` API. This change is aimed at enhancing the device identification process during payment requests.

## Business Rationale
The addition of the `BINDINGMODE` attribute is driven by the need to improve the granularity of device identification in payment transactions. This enhancement will allow for better tracking and categorization of payment requests based on the mode of communication used, thereby supporting regulatory compliance and improving user experience.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes to accommodate the new `BINDINGMODE` attribute:
- Update the `Device` element in the `ReqPay` API payload to include the `BINDINGMODE` attribute.
- Ensure that the `BINDINGMODE` attribute is mandatory and adheres to the allowed values: `MMS`, `SMS`, `RSMS`, and `SMV`.

## Schema Changes
The following changes have been made to the XSD schema:
- **Element Added**: `BINDINGMODE` attribute to the `Device` element.
  - **Data Type**: `xs:string`
  - **Mandatory**: Yes
  - **Allowed Values**: 
    - `MMS`
    - `SMS`
    - `RSMS`
    - `SMV`

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Effective Date**: [Insert effective date here]
- **Migration Steps**: Ensure that all systems are updated to handle the new `BINDINGMODE` attribute before the effective date.
- **Rollout Considerations**: Monitor the implementation for any issues related to the new attribute and provide support as needed during the transition period.