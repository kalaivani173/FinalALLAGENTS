package com.Bene.BeneficiaryBank.dto;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import javax.xml.bind.annotation.XmlAttribute;

class PayerTest {

    @Test
    void testBindingModeAttribute() {
        Payer payer = new Payer();
        payer.setBindingMode("MMS");
        assertEquals("MMS", payer.getBindingMode());

        payer.setBindingMode("SMS");
        assertEquals("SMS", payer.getBindingMode());

        payer.setBindingMode("RSMS");
        assertEquals("RSMS", payer.getBindingMode());

        payer.setBindingMode("SMV");
        assertEquals("SMV", payer.getBindingMode());
    }

    @Test
    void testBindingModeMandatory() {
        Payer payer = new Payer();
        assertThrows(IllegalArgumentException.class, () -> {
            payer.setBindingMode(null);
        });
    }
}