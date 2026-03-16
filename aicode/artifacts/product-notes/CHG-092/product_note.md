# Product Note: ReqMandate (CHG-092)

## Change Summary
The introduction of the `ReqMandate` API represents a significant enhancement to the UPI framework, allowing for the creation and management of mandates. This new API facilitates automated recurring payments, thereby improving user experience and operational efficiency for both consumers and merchants.

## Business Rationale
This change was implemented to meet the growing demand for automated payment solutions in the digital payment landscape. By enabling recurring transactions through mandates, the UPI ecosystem can better serve users who prefer subscription-based services, aligning with industry trends and regulatory requirements for seamless payment processing.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the `ReqMandate` API, ensuring that they can handle the new request format and associated data elements. Key implementation requirements include:

- Support for the new `ReqMandate` API endpoint.
- Validation of mandatory fields in the request payload, including `Head`, `Txn`, `Mandate`, `Amount`, `Payer`, and `Payee`.
- Proper handling of optional fields to enhance flexibility in transaction processing.

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
- **Migration Steps**: Ensure all systems are updated to support the new API and validate against the provided XSD schema.
- **Rollout Considerations**: Monitor transaction flows closely post-implementation to address any issues promptly and ensure compliance with regulatory standards.