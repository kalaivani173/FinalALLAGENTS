# Product Note: ReqPay (CHG-497)

## Change Summary
This document outlines the addition of a new XML attribute, `BINDINGMODE`, to the `Device` element within the `ReqPay` API. This change aims to enhance the data structure by allowing the specification of the binding mode used during transactions.

## Business Rationale
The addition of the `BINDINGMODE` attribute is driven by the need to provide more granular control over transaction processing methods. This change will facilitate better integration with various communication channels, particularly SMS, thereby improving user experience and operational efficiency.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the following changes in their systems:
- Update the `Device` element in the `ReqPay` API to include the new optional attribute `BINDINGMODE`.
- The `BINDINGMODE` attribute should accept the value "SMS" and is not mandatory.

## Schema Changes
The following changes have been made to the XSD schema:
- **Element Added**: `BINDINGMODE` attribute to the `Device` element.
  - **Data Type**: `xs:string`
  - **Mandatory**: No
  - **Allowed Values**: "SMS"

## Sample Payloads
No sample payloads were provided for this change.

## Go-Live Notes
- **Effective Date**: [Insert Go-Live Date]
- **Migration Steps**: Ensure that all systems are updated to accommodate the new `BINDINGMODE` attribute before the effective date.
- **Rollout Considerations**: Monitor transaction processing post-implementation to ensure that the new attribute is being utilized correctly and that there are no disruptions in service.