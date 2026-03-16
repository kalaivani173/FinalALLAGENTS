package com.example.upi;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import javax.xml.bind.annotation.XmlElement;
import javax.xml.bind.annotation.XmlElementWrapper;
import java.util.ArrayList;
import java.util.List;

class UpdatedCodeTest {

    @Test
    void testDelegateAttribute() {
        UpdatedCode updatedCode = new UpdatedCode();
        
        // Test default value
        assertNull(updatedCode.getDelegate());
        
        // Set delegate to "Y" and test
        updatedCode.setDelegate("Y");
        assertEquals("Y", updatedCode.getDelegate());
        
        // Set delegate to "N" and test
        updatedCode.setDelegate("N");
        assertEquals("N", updatedCode.getDelegate());
        
        // Test invalid value (not part of allowed values)
        updatedCode.setDelegate("Invalid");
        assertNotEquals("Invalid", updatedCode.getDelegate());
    }

    @Test
    void testPayeesList() {
        UpdatedCode updatedCode = new UpdatedCode();
        List<Payee> payees = new ArrayList<>();
        Payee payee = new Payee(); // Assuming Payee has a default constructor
        payees.add(payee);
        
        updatedCode.setPayees(payees);
        assertEquals(1, updatedCode.getPayees().size());
        assertSame(payee, updatedCode.getPayees().get(0));
    }
}