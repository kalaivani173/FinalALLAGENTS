# Product Note: ReqMandate (CHG-081)

## Change Summary
The introduction of the `ReqMandate` API allows for the creation and management of mandates within the UPI ecosystem. This new API facilitates the establishment of recurring payment agreements between payers and payees, enhancing the flexibility and functionality of UPI transactions.

## Business Rationale
This change was implemented to meet the growing demand for automated recurring payments in the digital payment landscape. By enabling mandates, the UPI framework aligns with industry trends and regulatory requirements, providing users with a seamless payment experience while ensuring compliance with financial regulations.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the `ReqMandate` API, which includes the following key components:
- Support for the new API endpoint to handle mandate requests.
- Validation of mandatory fields in the request payload, including attributes within the `Head`, `Txn`, `Mandate`, `Amount`, `Payer`, and `Payee` elements.
- Ensure that the API can process the specified attributes and their data types as defined in the XSD schema.

## Schema Changes
The following elements and attributes have been added in the XSD schema for the `ReqMandate` API:
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
- **Migration Steps**: Ensure all systems are updated to support the new `ReqMandate` API. Conduct thorough testing to validate the implementation.
- **Rollout Considerations**: Monitor the initial usage of the API for any issues and gather feedback for future enhancements.