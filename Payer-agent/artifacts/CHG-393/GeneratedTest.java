package com.payer.PayerPSP.dto;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import jakarta.xml.bind.annotation.XmlAttribute;

public class PayerTest {

    @Test
    public void testBindingModeAttribute() {
        Payer payer = new Payer();
        String expectedBindingMode = "SMS";
        
        payer.setBindingMode(expectedBindingMode);
        
        assertEquals(expectedBindingMode, payer.getBindingMode());
    }

    @Test
    public void testBindingModeAttributeMandatory() {
        Payer payer = new Payer();
        
        assertThrows(NullPointerException.class, () -> {
            payer.setBindingMode(null);
            payer.getBindingMode();
        });
    }

    @Test
    public void testAllowedValuesForBindingMode() {
        Payer payer = new Payer();
        
        String[] allowedValues = {"SMS", "RSMS", "SMV"};
        
        for (String value : allowedValues) {
            payer.setBindingMode(value);
            assertEquals(value, payer.getBindingMode());
        }
    }
}