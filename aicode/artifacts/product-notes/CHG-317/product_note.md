# Product Note: ReqMandate (CHG-317)

## Change Summary
The introduction of the `ReqMandate` API represents a significant enhancement to the UPI framework, allowing for the creation and management of mandates. This new API facilitates automated recurring payments, thereby improving user experience and operational efficiency for both payers and payees.

## Business Rationale
This change was implemented to meet the growing demand for automated payment solutions in the digital payment landscape. By enabling recurring transactions through mandates, the UPI ecosystem can better serve businesses and consumers, aligning with regulatory requirements and enhancing overall transaction security and convenience.

## PSP/Bank Implementation Requirements
PSPs and banks must implement the `ReqMandate` API as part of their UPI offerings. This includes:
- Integrating the new API endpoint for processing mandate requests.
- Ensuring compliance with the defined XSD schema for the `ReqMandate` structure.
- Updating their systems to handle the new transaction types and attributes associated with mandates.

## Schema Changes
The XSD schema for the `ReqMandate` API includes the following elements:
- **New Elements**:
  - `ReqMandate`: The root element containing the mandate request structure.
  - `Head`, `Txn`, `Mandate`, `Amount`, `Payer`, and `Payee`: Child elements that define the transaction details, payer and payee information, and mandate specifics.
  
- **Attributes**:
  - Various attributes have been defined for each element, such as `ver`, `ts`, `orgId`, `msgId` for `Head`, and attributes related to the mandate, payer, and payee details.

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
- **Migration Steps**: PSPs and banks should ensure that their systems are updated to support the new API by the go-live date. Testing should be conducted to validate the integration and compliance with the new schema.
- **Rollout Considerations**: It is recommended to communicate with all stakeholders regarding the new API capabilities and provide necessary training to ensure smooth adoption.