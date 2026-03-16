# Product Note: ReqPay (CHG-346)

## Change Summary
This document outlines the addition of a new XML attribute, "delegate," to the ReqPay API under the Txn element. This change is designed to enhance the functionality of the API by allowing the specification of delegation in transaction requests.

## Business Rationale
The addition of the "delegate" attribute is aimed at improving transaction management and flexibility for users. By enabling the delegation of transactions, this change addresses a growing need for more nuanced transaction handling in the UPI ecosystem, thereby enhancing user experience and operational efficiency.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes to accommodate the new "delegate" attribute:
- Update the ReqPay API to include the "delegate" attribute within the Txn element.
- The "delegate" attribute is of type `xs:string`, is optional, and can take the values "Y" (Yes) or "N" (No).

## Schema Changes
The following changes have been made to the XSD schema:
- **Element**: Txn
  - **Attribute Added**: 
    - **Name**: delegate
    - **Type**: xs:string
    - **Mandatory**: false
    - **Allowed Values**: "Y", "N"

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Effective Date**: [Insert effective date here]
- **Migration Steps**: Ensure that all systems interacting with the ReqPay API are updated to handle the new "delegate" attribute.
- **Rollout Considerations**: Monitor transaction processing for any issues related to the new attribute post-implementation.