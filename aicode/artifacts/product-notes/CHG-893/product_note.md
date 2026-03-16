# Product Note: ReqMandate (CHG-893)

## Change Summary
The addition of the new API, `ReqMandate`, aims to facilitate the management of mandates within the UPI ecosystem. This API will enable users to create, modify, and manage payment mandates efficiently.

## Business Rationale
This change was implemented to enhance the UPI product offering by providing a structured way to handle payment mandates. It addresses the growing need for recurring payment solutions in various sectors, including subscriptions and services, thereby improving user experience and operational efficiency.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the `ReqMandate` API as per the provided XSD schema. This includes ensuring that all mandatory fields are correctly populated in the requests and that the API can handle the specified attributes for transactions, mandates, amounts, payers, and payees.

## Schema Changes
The following elements and attributes have been defined in the new XSD schema for the `ReqMandate` API:
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
The `ReqMandate` API is scheduled to go live on [insert go-live date]. PSPs and banks are advised to complete their implementation and testing by this date to ensure a smooth transition. Migration steps should include updating existing systems to accommodate the new API and conducting thorough testing to validate functionality.