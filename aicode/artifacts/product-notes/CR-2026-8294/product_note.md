# Product Note: ReqPay (CR-2026-8294)

## Change Summary
This document outlines the addition of a new XML attribute, `delegate`, to the ReqPay API under the UPI sub-product. This change aims to enhance the transaction capabilities by allowing the specification of delegation in transaction requests.

## Business Rationale
The addition of the `delegate` attribute is intended to meet evolving product needs within the UPI framework. By enabling this feature, the API can better accommodate scenarios where transaction delegation is necessary, thereby improving flexibility and user experience.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes in their systems:
- Update the ReqPay API to include the new optional XML attribute `delegate` within the `Txn` element.
- The `delegate` attribute should accept values of either "y" or "n" to indicate whether delegation is applicable for the transaction.

## Schema Changes
The following changes have been made to the XSD schema:
- **New Attribute Added**: 
  - `delegate` (type: `xs:string`, optional) added to the `Txn` element.

## Sample Payloads
No sample payloads were provided for this change.

## Go-Live Notes
- **Effective Date**: The change will be effective immediately upon deployment.
- **Migration Steps**: Ensure that all systems interacting with the ReqPay API are updated to handle the new `delegate` attribute.
- **Rollout Considerations**: Monitor transaction requests for compliance with the new attribute and provide support for any issues arising from the implementation.