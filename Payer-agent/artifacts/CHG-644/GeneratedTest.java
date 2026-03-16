package com.payer.PayerPSP.dto;

import jakarta.xml.bind.JAXBContext;
import jakarta.xml.bind.JAXBException;
import jakarta.xml.bind.Marshaller;
import jakarta.xml.bind.Unmarshaller;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

import java.io.StringReader;
import java.io.StringWriter;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

@SpringBootTest
class PayerTest {

    @Test
    void testBindingModeSerialization() throws JAXBException {
        Payer payer = new Payer();
        payer.setBindingMode("MMS");

        JAXBContext context = JAXBContext.newInstance(Payer.class);
        Marshaller marshaller = context.createMarshaller();
        marshaller.setProperty(Marshaller.JAXB_FORMATTED_OUTPUT, true);

        StringWriter writer = new StringWriter();
        marshaller.marshal(payer, writer);
        String xmlOutput = writer.toString();

        assertEquals(true, xmlOutput.contains("BINDINGMODE=\"MMS\""));
    }

    @Test
    void testBindingModeDeserialization() throws JAXBException {
        String xmlInput = "<Payer BINDINGMODE=\"SMS\"></Payer>";

        JAXBContext context = JAXBContext.newInstance(Payer.class);
        Unmarshaller unmarshaller = context.createUnmarshaller();
        Payer payer = (Payer) unmarshaller.unmarshal(new StringReader(xmlInput));

        assertEquals("SMS", payer.getBindingMode());
    }

    @Test
    void testBindingModeMandatory() {
        Payer payer = new Payer();
        assertThrows(NullPointerException.class, () -> {
            String bindingMode = payer.getBindingMode();
            if (bindingMode == null) {
                throw new NullPointerException("BINDINGMODE is mandatory");
            }
        });
    }
}