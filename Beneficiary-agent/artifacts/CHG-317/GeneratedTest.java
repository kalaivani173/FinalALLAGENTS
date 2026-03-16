package com.Bene.BeneficiaryBank.controller;

import com.Bene.BeneficiaryBank.dto.ReqMandate;
import com.Bene.BeneficiaryBank.service.HbtService;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.client.RestTemplate;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

class HbtControllerTest {

    @InjectMocks
    private HbtController hbtController;

    @Mock
    private HbtService hbtService;

    @Mock
    private RestTemplate restTemplate;

    public HbtControllerTest() {
        MockitoAnnotations.openMocks(this);
    }

    @Test
    void testCreateReqMandate() throws Exception {
        String custRef = "testCustRef";
        ReqMandate reqMandate = new ReqMandate();
        reqMandate.setTxn(new Txn());
        reqMandate.getTxn().setId("testTxnId");

        when(hbtService.createReqMandate(custRef)).thenReturn(reqMandate);
        when(restTemplate.postForEntity(any(String.class), any(HttpEntity.class), eq(String.class)))
                .thenReturn(ResponseEntity.ok("<response>Success</response>"));

        hbtController.createReqMandate(custRef);

        verify(hbtService, times(1)).createReqMandate(custRef);
        verify(restTemplate, times(1)).postForEntity(eq("http://localhost:8081/upi/ReqMandate/2.0/urn:txnid:testTxnId"), any(HttpEntity.class), eq(String.class));
    }
}