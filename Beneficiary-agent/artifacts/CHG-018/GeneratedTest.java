package com.example.upi;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

import javax.xml.bind.annotation.XmlAttribute;
import javax.xml.bind.annotation.XmlElement;
import javax.xml.bind.annotation.XmlElementWrapper;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;

@SpringBootTest
class Updated_Code {

    @XmlElement(name = "Payer")
    private Payer payer;

    @XmlAttribute(name = "BINDINGMODE")
    private String bindingMode;

    @XmlElementWrapper(name = "Payees")
    @XmlElement(name = "Payee")
    private List<Payee> payees;

    // Getters and Setters
    public String getBindingMode() {
        return bindingMode;
    }

    public void setBindingMode(String bindingMode) {
        this.bindingMode = bindingMode;
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

    @Test
    void testBindingModeAttribute() {
        Updated_Code updatedCode = new Updated_Code();
        updatedCode.setBindingMode("MMS");
        assertEquals("MMS", updatedCode.getBindingMode());

        updatedCode.setBindingMode("SMS");
        assertEquals("SMS", updatedCode.getBindingMode());
    }
}