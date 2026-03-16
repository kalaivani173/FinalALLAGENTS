package com.payee.psp.dto;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class TxnTest {

    @Test
    void testDelegateAttribute() {
        Txn txn = new Txn();
        
        // Test setting and getting the delegate attribute
        txn.setDelegate("Y");
        assertEquals("Y", txn.getDelegate());

        txn.setDelegate("N");
        assertEquals("N", txn.getDelegate());

        // Test setting an invalid value (not part of allowed values)
        txn.setDelegate(null);
        assertNull(txn.getDelegate());
    }

    @Test
    void testRiskScoresAttribute() {
        Txn txn = new Txn();
        RiskScores riskScores = new RiskScores(); // Assuming RiskScores is a valid class
        txn.setRiskScores(riskScores);
        
        assertNotNull(txn.getRiskScores());
        assertEquals(riskScores, txn.getRiskScores());
    }

    @Test
    void testCustRefAttribute() {
        Txn txn = new Txn();
        txn.setCustRef("12345");
        
        assertEquals("12345", txn.getCustRef());
    }

    @Test
    void testIdAttribute() {
        Txn txn = new Txn();
        txn.setId("txn-001");
        
        assertEquals("txn-001", txn.getId());
    }
}