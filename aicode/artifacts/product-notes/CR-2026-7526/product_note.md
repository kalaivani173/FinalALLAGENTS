# Product Note: ReqPay (CR-2026-7526)

## Change Summary
This document outlines the addition of a new XML attribute, `bindingmode`, to the `Device` element in the ReqPay API. This change is part of the UPI sub-product enhancements aimed at improving transaction handling and flexibility.

## Business Rationale
The introduction of the `bindingmode` attribute is intended to enhance the functionality of the ReqPay API by allowing for more versatile transaction processing methods. This change addresses the need for improved communication modes, specifically through SMS and RSMS, thereby aligning with evolving user requirements and regulatory standards.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes in their systems:
- Update the XML schema to include the new `bindingmode` attribute within the `Device` element.
- The `bindingmode` attribute is of type `xs:string`, is optional, and can take the following values:
  - `sms`
  - `rsms`

## Schema Changes
The following changes have been made to the XSD schema:
- **Element Modified**: `Device`
  - **New Attribute Added**: `bindingmode` (optional, type: `bindingmodeType`)
- **New Simple Type**: `bindingmodeType` with allowed values:
  - `sms`
  - `rsms`

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Effective Date**: [Insert effective date here]
- **Migration Steps**: Ensure that all systems are updated to accommodate the new `bindingmode` attribute before the effective date.
- **Rollout Considerations**: Monitor transaction processing post-implementation to ensure that the new attribute is functioning as intended and that all PSPs and banks are compliant with the updated schema.