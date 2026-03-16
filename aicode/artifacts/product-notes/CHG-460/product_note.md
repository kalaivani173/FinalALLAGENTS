# Product Note: ReqPay (CHG-460)

## Change Summary
This document outlines the addition of a new XML attribute, `delegate`, to the `Txn` element in the ReqPay API. The `delegate` attribute is designed to facilitate the delegation of payments, allowing for more flexible transaction handling.

## Business Rationale
The introduction of the `delegate` attribute addresses the need for enhanced payment delegation capabilities within the UPI framework. This change is aimed at improving user experience and operational efficiency for payment service providers (PSPs) and banks, enabling them to better manage delegated transactions.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes to accommodate the new `delegate` attribute:
- Update the `Txn` element in the ReqPay API to include the `delegate` attribute.
- The `delegate` attribute is of type `xs:string`, is optional, and can take the values "Y" (Yes) or "N" (No).

## Schema Changes
The following changes have been made to the XSD schema:
- **Element**: `Txn`
  - **New Attribute**: `delegate`
    - **Type**: `xs:string`
    - **Mandatory**: No
    - **Allowed Values**: "Y", "N"

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Go-Live Date**: [Insert Go-Live Date]
- **Migration Steps**: Ensure that all systems are updated to recognize the new `delegate` attribute in the ReqPay API.
- **Rollout Considerations**: Monitor transaction handling post-implementation to ensure that the delegation functionality operates as intended.