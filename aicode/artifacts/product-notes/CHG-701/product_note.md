# Product Note: ReqMandate (CHG-701)

## Change Summary
The UPI system is introducing a new API named `ReqMandate` to facilitate the management of mandates within the payment ecosystem. This addition aims to enhance the capabilities of payment service providers (PSPs) and banks in handling recurring payment agreements.

## Business Rationale
The addition of the `ReqMandate` API is driven by the need for a standardized approach to manage mandates, which are essential for recurring payments. This change aligns with regulatory requirements and addresses the growing demand for automated payment solutions in the digital payment landscape.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the `ReqMandate` API as per the provided schema. Key requirements include:
- Integration of the new API endpoint to handle mandate requests.
- Adherence to the specified XML schema for request and response formats.
- Validation of mandatory fields in the payload, including attributes in the `Head`, `Txn`, `Mandate`, `Amount`, `Payer`, and `Payee` elements.

## Schema Changes
The following elements and attributes have been defined in the new XSD schema for the `ReqMandate` API:
- **Elements**:
  - `ReqMandate`
    - `Head`
    - `Txn`
    - `Mandate`
    - `Amount`
    - `Payer`
    - `Payee`
- **Attributes**:
  - `Head`: `ver`, `ts`, `orgId`, `msgId`
  - `Txn`: `id`, `note`, `refId`, `refUrl`, `ts`, `type`
  - `Mandate`: `name`, `type`, `recurrence`, `rule`, `startDate`, `endDate`, `expiry`, `revocable`, `shareToPayee`
  - `Amount`: `value`, `curr`
  - `Payer`: `addr`, `name`, `seqNum`, `type`
  - `Payee`: `addr`, `name`, `type`

## Sample Payloads
A sample request payload for the `ReqMandate` API is provided below:

```xml
<ReqMandate xmlns="http://npci.org/upi/schema/">
    <Head ver="1.0" ts="2026-01-28T12:30:00" orgId="HDFC" msgId="MSG123456"/>
    
    <Txn id="TXN987654"
         note="Monthly Subscription"
         refId="REF12345"
         refUrl="https://merchant.example.com"
         ts="2026-01-28T12:30:00"
         type="MANDATE"/>

    <Mandate name="OTT Subscription"
             type="CREATE"
             recurrence="MONTHLY"
             rule="MAX"
             startDate="2026-02-01"
             endDate="2027-01-31"
             expiry="2027-01-31"
             revocable="Y"
             shareToPayee="Y"/>

    <Amount value="499.00" curr="INR"/>

    <Payer addr="user@upi"
           name="Rahul Sharma"
           seqNum="1"
           type="PERSON">
        <Info>
            <Identity type="ACCOUNT" verifiedName="Rahul Sharma"/>
        </Info>
    </Payer>

    <Payee addr="merchant@upi"
           name="Example OTT Pvt Ltd"
           type="MERCHANT"/>
</ReqMandate>
```

## Go-Live Notes
- **Go-Live Date**: [Insert Go-Live Date]
- **Migration Steps**: Ensure all systems are updated to support the new API and validate against the provided schema.
- **Rollout Considerations**: Monitor the implementation for compliance with the new mandate management processes and provide support for any integration issues that may arise.