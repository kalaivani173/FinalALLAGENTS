# Product Note: ReqPay (CR-2026-5979)

## Change Summary
This document outlines the addition of a new XML attribute, `delegate`, to the `Txn` element in the ReqPay API. This change is intended to enhance the functionality of the API by allowing for additional transaction metadata.

## Business Rationale
The addition of the `delegate` attribute is driven by the need to provide more granular control and information regarding transaction processing. This change aims to improve transaction handling and reporting capabilities for Payment Service Providers (PSPs) and banks.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes in their systems:
- Update the XML payload structure to include the new optional attribute `delegate` within the `Txn` element.
- Ensure that the `delegate` attribute can accept values of "Y" or "N".

## Schema Changes
The following changes have been made to the XSD schema:
- **New Attribute Added**: 
  - `delegate` (type: `xs:string`, optional) added to the `Txn` element.

## Sample Payloads
No sample payloads were provided for this change. Please refer to the updated XSD schema for guidance on the new attribute.

## Go-Live Notes
- **Effective Date**: The change will be effective immediately upon deployment.
- **Migration Steps**: Ensure that all systems are updated to accommodate the new `delegate` attribute before the go-live date.
- **Rollout Considerations**: Testing should be conducted to verify that the new attribute is correctly integrated and that existing functionalities remain unaffected.