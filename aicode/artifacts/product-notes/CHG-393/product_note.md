# Product Note: ReqPay (CHG-393)

## Change Summary
This document outlines the addition of a new XML attribute, `BINDINGMODE`, to the `Device` element within the `ReqPay` API. This change is aimed at enhancing the data structure to accommodate new binding modes for device identification.

## Business Rationale
The addition of the `BINDINGMODE` attribute is driven by the need to standardize device identification methods across various payment systems. This change will facilitate better tracking and management of transactions initiated from different devices, thereby improving security and user experience.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes in their systems:
- Update the `ReqPay` API to include the new `BINDINGMODE` attribute within the `Device` element.
- Ensure that the `BINDINGMODE` attribute is marked as mandatory and accepts only the following values: `SMS`, `RSMS`, and `SMV`.

## Schema Changes
The following changes have been made to the XSD schema:
- **Element Added**: `BINDINGMODE` attribute to the `Device` element.
  - **Data Type**: `xs:string`
  - **Mandatory**: Yes
  - **Allowed Values**: `SMS`, `RSMS`, `SMV`

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Effective Date**: [Insert effective date here]
- **Migration Steps**: Ensure that all systems are updated to handle the new `BINDINGMODE` attribute before the effective date.
- **Rollout Considerations**: Monitor transaction flows post-implementation to ensure compliance with the new attribute requirements.