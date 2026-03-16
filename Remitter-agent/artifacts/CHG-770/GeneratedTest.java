package com.example.upi.remitterbank;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

import javax.xml.bind.annotation.XmlAttribute;
import javax.xml.bind.annotation.XmlElement;
import javax.xml.bind.annotation.XmlElementWrapper;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertNotNull;

@SpringBootTest
class Updated_Code {

    @XmlElement(name = "Payer")
    private Payer payer;

    @XmlAttribute(name = "delegate")
    private String delegate;

    @XmlElementWrapper(name = "Payees")
    @XmlElement(name = "Payee")
    private List<Payee> payees;

    @Test
    void testDelegateAttributeIsNotNull() {
        Updated_Code updatedCode = new Updated_Code();
        updatedCode.delegate = "testDelegate";
        assertNotNull(updatedCode.delegate);
    }

    @Test
    void testPayeesListIsNotNull() {
        Updated_Code updatedCode = new Updated_Code();
        updatedCode.payees = List.of(new Payee());
        assertNotNull(updatedCode.payees);
    }
}