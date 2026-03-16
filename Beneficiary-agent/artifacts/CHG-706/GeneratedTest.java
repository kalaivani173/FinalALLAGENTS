package com.Bene.BeneficiaryBank.dto;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import jakarta.xml.bind.JAXBContext;
import jakarta.xml.bind.JAXBException;
import jakarta.xml.bind.Marshaller;
import jakarta.xml.bind.Unmarshaller;
import java.io.StringReader;
import java.io.StringWriter;

public class ReqPayTest {

    @Test
    public void testDelegateAttributeSerialization() throws JAXBException {
        ReqPay reqPay = new ReqPay();
        reqPay.setDelegate("Y");

        JAXBContext jaxbContext = JAXBContext.newInstance(ReqPay.class);
        Marshaller marshaller = jaxbContext.createMarshaller();
        marshaller.setProperty(Marshaller.JAXB_FORMATTED_OUTPUT, Boolean.TRUE);

        StringWriter stringWriter = new StringWriter();
        marshaller.marshal(reqPay, stringWriter);
        String xmlOutput = stringWriter.toString();

        assertTrue(xmlOutput.contains("delegate=\"Y\""));
    }

    @Test
    public void testDelegateAttributeDeserialization() throws JAXBException {
        String xmlInput = "<ReqPay xmlns=\"http://npci.org/upi/schema/\" delegate=\"N\"><Payer></Payer></ReqPay>";

        JAXBContext jaxbContext = JAXBContext.newInstance(ReqPay.class);
        Unmarshaller unmarshaller = jaxbContext.createUnmarshaller();
        ReqPay reqPay = (ReqPay) unmarshaller.unmarshal(new StringReader(xmlInput));

        assertEquals("N", reqPay.getDelegate());
    }

    @Test
    public void testDelegateAttributeDefaultValue() {
        ReqPay reqPay = new ReqPay();
        assertNull(reqPay.getDelegate());
    }
}