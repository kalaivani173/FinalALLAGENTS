# Product Note: ReqMandate (CHG-263)

## Change Summary
The introduction of the `ReqMandate` API allows for the creation and management of payment mandates within the UPI ecosystem. This new API facilitates recurring payment setups, enhancing the flexibility and functionality of UPI transactions.

## Business Rationale
The addition of the `ReqMandate` API addresses the growing demand for automated and recurring payment solutions in the digital payment landscape. This change is driven by the need to streamline payment processes for consumers and merchants, thereby improving user experience and operational efficiency.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the `ReqMandate` API to support the creation and management of payment mandates. This includes handling the following elements and attributes as defined in the XSD schema:
- **Head**: Required attributes include `ver`, `ts`, `orgId`, and `msgId`.
- **Txn**: Required attributes include `id`, `ts`, and `type`. Optional attributes include `note`, `refId`, and `refUrl`.
- **Mandate**: Required attributes include `name`, `type`, `recurrence`, `rule`, `startDate`, `endDate`, and `expiry`. Optional attributes include `revocable` and `shareToPayee`.
- **Amount**: Required attributes include `value` and `curr`.
- **Payer**: Required attributes include `addr`, `name`, `seqNum`, and `type`. The `Info` element must include an `Identity` with required attributes `type` and `verifiedName`.
- **Payee**: Required attributes include `addr`, `name`, and `type`.

## Schema Changes
The `ReqMandate` API introduces the following elements and attributes in the XSD schema:
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
The `ReqMandate` API is scheduled for rollout on [insert go-live date]. PSPs and banks are advised to complete their implementation and testing by this date to ensure a smooth transition. Migration steps should include updating existing systems to accommodate the new API and conducting thorough testing to validate functionality.