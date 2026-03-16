# Product Note: ReqMandate (CHG-662)

## Change Summary
The introduction of the `ReqMandate` API allows for the creation and management of mandates within the UPI ecosystem. This new API facilitates the automation of recurring payments, enhancing the user experience for both payers and payees.

## Business Rationale
This change was implemented to meet the growing demand for automated payment solutions in the digital payment landscape. By enabling mandates, the UPI framework aligns with regulatory requirements and enhances the product offering for banks and payment service providers (PSPs).

## PSP/Bank Implementation Requirements
PSPs and banks must implement the `ReqMandate` API, ensuring that they can handle the new payload structure and adhere to the defined XSD schema. This includes processing the mandatory fields within the `Head`, `Txn`, `Mandate`, `Amount`, `Payer`, and `Payee` elements as specified in the schema.

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
The `ReqMandate` API is scheduled to go live on **February 1, 2026**. All PSPs and banks must ensure that their systems are updated and tested for compliance with the new API specifications prior to this date. Migration steps should include thorough testing of the API endpoints and validation of the payload structure against the provided XSD schema.