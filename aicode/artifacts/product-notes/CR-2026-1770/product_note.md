# Product Note: ReqMandate (CR-2026-1770)

## Change Summary
This document outlines the addition of a new XML attribute, `note`, to the `Head` element of the `ReqMandate` API. This change is intended to enhance the functionality of the API by allowing the inclusion of a note that can indicate specific information related to the mandate request.

## Business Rationale
The addition of the `note` attribute is driven by the need for improved communication and clarity in mandate requests. By allowing a note to be included, PSPs and banks can provide additional context or instructions that may be necessary for processing mandates effectively.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes to accommodate the new `note` attribute:
- Update the XML schema to include the `note` attribute in the `Head` element of the `ReqMandate` API.
- Ensure that the `note` attribute is optional and can accept values of "y" or "n".

## Schema Changes
The following changes have been made to the XSD schema:
- **Element Modified**: `Head`
  - **New Attribute Added**: `note` (optional, type: `xs:string`, allowed values: "y/n")

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Effective Date**: Please refer to the official communication for the go-live date.
- **Migration Steps**: Ensure that your systems are updated to handle the new `note` attribute as specified in the updated XSD schema.
- **Rollout Considerations**: Testing should be conducted to verify that the new attribute is correctly processed in all relevant scenarios.