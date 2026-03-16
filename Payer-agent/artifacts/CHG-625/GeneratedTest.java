package com.payer.PayerPSP.dto;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class PayerTest {

    @Test
    void testBindingModeAttribute() {
        Payer payer = new Payer();
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
        assertThrows(NullPointerException.class, () -> {
            payer.setBindingMode(null);
        });
    }
}