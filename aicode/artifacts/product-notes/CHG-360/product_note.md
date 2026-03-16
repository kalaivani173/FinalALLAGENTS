# Product Note: ReqMandate (CHG-360)

## Change Summary
The introduction of the new API, `ReqMandate`, aims to facilitate the creation and management of mandates within the UPI ecosystem. This API will enable users to set up recurring payments with specified parameters, enhancing the overall payment experience.

## Business Rationale
This change was made to address the growing demand for automated recurring payment solutions in the digital payment landscape. By implementing the `ReqMandate` API, we aim to provide a seamless and efficient way for users to manage their subscriptions and recurring transactions, thereby improving customer satisfaction and engagement.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the `ReqMandate` API as per the defined schema. Key requirements include:
- Support for the new XML structure as defined in the XSD schema.
- Ensure that all mandatory fields are validated and processed correctly.
- Update systems to handle the new transaction types associated with mandates.

## Schema Changes
The following elements and attributes have been added in the new XSD schema for the `ReqMandate` API:
- **Elements**:
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
- **Migration Steps**: Ensure all systems are updated to support the new API and validate against the provided XSD schema.
- **Rollout Considerations**: Monitor the initial transactions closely for any issues and provide support for any queries related to the new API.