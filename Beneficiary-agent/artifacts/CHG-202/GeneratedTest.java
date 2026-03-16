package com.example.upi;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

import javax.xml.bind.annotation.XmlAttribute;
import javax.xml.bind.annotation.XmlElement;
import javax.xml.bind.annotation.XmlElementWrapper;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;

@SpringBootTest
class UpdatedCodeTest {

    @Test
    void testDelegateAttribute() {
        UpdatedCode updatedCode = new UpdatedCode();
        
        updatedCode.setDelegate("Y");
        assertEquals("Y", updatedCode.getDelegate());
        
        updatedCode.setDelegate("N");
        assertEquals("N", updatedCode.getDelegate());
        
        updatedCode.setDelegate(null);
        assertEquals(null, updatedCode.getDelegate());
    }
}

class UpdatedCode {
    @XmlElement(name = "Head")
    private Head head;

    @XmlElement(name = "Txn")
    private Txn txn;

    @XmlElement(name = "Payer")
    private Payer payer;

    @XmlElementWrapper(name = "Payees")
    @XmlElement(name = "Payee")
    private List<Payee> payees;

    @XmlAttribute(name = "delegate")
    private String delegate;

    // getters/setters

    public Head getHead() {
        return head;
    }

    public void setHead(Head head) {
        this.head = head;
    }

    public Txn getTxn() {
        return txn;
    }

    public void setTxn(Txn txn) {
        this.txn = txn;
    }

    public Payer getPayer() {
        return payer;
    }

    public void setPayer(Payer payer) {
        this.payer = payer;
    }

    public List<Payee> getPayees() {
        return payees;
    }

    public void setPayees(List<Payee> payees) {
        this.payees = payees;
    }

    public String getDelegate() {
        return delegate;
    }

    public void setDelegate(String delegate) {
        this.delegate = delegate;
    }
}