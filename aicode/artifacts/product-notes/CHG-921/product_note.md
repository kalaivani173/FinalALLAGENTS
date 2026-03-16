# Product Note: ReqPay (CHG-921)

## Change Summary
The UPI system is introducing a new API named `ReqPay`, aimed at enhancing payment request functionalities. This addition is designed to streamline the process of initiating payment mandates, thereby improving user experience and operational efficiency.

## Business Rationale
The introduction of the `ReqPay` API is driven by the need to support recurring payment mandates in a more structured manner. This change aligns with evolving market demands for automated payment solutions and regulatory requirements for secure and efficient transaction processing.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the new `ReqPay` API, ensuring that they can handle the following elements and attributes as defined in the XSD schema:
- **Head**: Required attributes include `ver`, `ts`, `orgId`, and `msgId`.
- **Txn**: Required attributes include `id`, `ts`, and `type`. Optional attributes are `note`, `refId`, and `refUrl`.
- **Mandate**: Required attributes include `name`, `type`, `recurrence`, `rule`, `startDate`, `endDate`, and `expiry`. Optional attributes are `revocable` and `shareToPayee`.
- **Amount**: Required attributes include `value` and `curr`.
- **Payer**: Required attributes include `addr`, `name`, and `type`. Optional attributes are `seqNum`.
- **Payee**: Required attributes include `addr`, `name`, and `type`.

## Schema Changes
The XSD schema for the `ReqPay` API includes the following elements and attributes:
- **New Elements**:
  - `ReqPay`
  - `Head`
  - `Txn`
  - `Mandate`
  - `Amount`
  - `Payer`
  - `Payee`
- **Attributes**:
  - Various required and optional attributes have been defined for each element as detailed above.

## Sample Payloads
A sample request payload for the `ReqPay` API is provided below:

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
The `ReqPay` API is scheduled for rollout on [insert go-live date]. PSPs and banks are advised to complete their implementation and testing by this date to ensure a smooth transition. Migration steps should include updating existing systems to accommodate the new API and conducting thorough testing to validate functionality.