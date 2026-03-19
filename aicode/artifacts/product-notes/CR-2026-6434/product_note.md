# Product Note: ReqPay (CR-2026-6434)

## Change Summary
This document outlines the addition of a new XML attribute, `delegate`, to the ReqPay API under the UPI sub-product. This change aims to enhance the transaction capabilities by allowing the specification of delegation in payment requests.

## Business Rationale
The addition of the `delegate` attribute is driven by the need to support more complex transaction scenarios within the UPI framework. This enhancement allows for better handling of transactions where delegation is necessary, thereby improving the overall user experience and compliance with evolving payment needs.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes in their systems:
- Update the ReqPay API to include the new optional XML attribute `delegate` within the `Txn` element.
- The `delegate` attribute should accept values of "Y" or "N" to indicate whether delegation is applicable for the transaction.

## Schema Changes
The following changes have been made to the XSD schema:
- **New Attribute Added**: 
  - `delegate` (type: `xs:string`, optional) added to the `Txn` element.

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Effective Date**: The change will be effective immediately upon deployment.
- **Migration Steps**: PSPs and banks should ensure their systems are updated to accommodate the new attribute before the next scheduled transaction processing cycle.
- **Rollout Considerations**: Testing should be conducted to ensure compatibility with existing systems and to validate the correct handling of the new `delegate` attribute.