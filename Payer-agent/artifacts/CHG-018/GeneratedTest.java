package com.payer.PayerPSP.dto;

import jakarta.xml.bind.JAXBContext;
import jakarta.xml.bind.JAXBException;
import jakarta.xml.bind.Marshaller;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

import static org.junit.jupiter.api.Assertions.assertEquals;

@SpringBootTest
public class PayerTest {

    @Test
    public void testBindingModeAttribute() throws JAXBException {
        Payer payer = new Payer();
        payer.setAddr("123 Main St");
        payer.setBindingMode("MMS");

        JAXBContext jaxbContext = JAXBContext.newInstance(Payer.class);
        Marshaller marshaller = jaxbContext.createMarshaller();
        marshaller.setProperty(Marshaller.JAXB_FORMATTED_OUTPUT, true);

        StringWriter writer = new StringWriter();
        marshaller.marshal(payer, writer);
        String xmlOutput = writer.toString();

        assertTrue(xmlOutput.contains("BINDINGMODE=\"MMS\""));
    }

    @Test
    public void testBindingModeAllowedValues() {
        Payer payer = new Payer();
        payer.setBindingMode("SMS");
        assertEquals("SMS", payer.getBindingMode());
    }

    @Test
    public void testBindingModeNotMandatory() {
        Payer payer = new Payer();
        payer.setAddr("456 Another St");
        assertNull(payer.getBindingMode());
    }
}