# Product Note: ReqPay (CR-2026-3208)

## Change Summary
This document outlines the addition of a new XML attribute, "SubProduct," to the ReqPay API, enabling the use of a UPI credit line on Rupay transactions. This change aims to enhance the functionality of the UPI system by allowing for credit line transactions.

## Business Rationale
The introduction of the "SubProduct" attribute is driven by the need to support credit line transactions within the UPI framework, particularly for Rupay. This change aligns with the evolving landscape of digital payments and the increasing demand for credit facilities in UPI transactions.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes in their systems:
- Update the ReqPay API to include the new optional XML attribute "SubProduct" within the "Txn" element.
- Ensure that the "SubProduct" attribute can accept the value "CreditLine."
- Validate that the attribute is not mandatory, allowing for backward compatibility with existing implementations.

## Schema Changes
The following changes have been made to the XSD schema:
- **New Attribute Added**: 
  - `SubProduct` (optional) of type `SubProductType` added to the `Txn` element.
- **SubProductType**: A new simple type defined with an enumeration value of "CreditLine."

## Sample Payloads
No sample payloads have been provided for this change.

## Go-Live Notes
- **Go-Live Date**: [Insert Go-Live Date]
- **Migration Steps**: Ensure that all systems are updated to accommodate the new "SubProduct" attribute before the go-live date.
- **Rollout Considerations**: Monitor transaction flows post-implementation to ensure that the new attribute is functioning as intended and that there are no disruptions in service.