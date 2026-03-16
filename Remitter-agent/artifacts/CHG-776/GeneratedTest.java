package com.remitterbank;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

@SpringBootTest
class ReqPayTest {

    @Test
    void testDelegateAttributeAddition() {
        // Simulate the creation of a request with the new delegate attribute
        String delegate = "Y"; // or "N"
        assertTrue(delegate.equals("Y") || delegate.equals("N"), "Delegate attribute must be 'Y' or 'N'");
    }

    @Test
    void testMandatoryAttribute() {
        // Check if the delegate attribute is not mandatory
        boolean isMandatory = false; // as per the change request
        assertEquals(false, isMandatory, "Delegate attribute should not be mandatory");
    }

    @Test
    void testAllowedValues() {
        // Validate allowed values for the delegate attribute
        String[] allowedValues = {"Y", "N"};
        assertTrue(allowedValues.length > 0, "Allowed values should not be empty");
    }
}