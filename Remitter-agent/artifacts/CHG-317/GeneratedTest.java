package com.remitter.RemitterBank.controller;

import com.remitter.RemitterBank.dto.ReqMandate;
import com.remitter.RemitterBank.service.ReqMandateService;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.client.RestTemplate;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@SpringBootTest
public class ReqMandateControllerTest {

    @Mock
    private ReqMandateService reqMandateService;

    @Mock
    private RestTemplate restTemplate;

    @InjectMocks
    @Autowired
    private ReqMandateController reqMandateController;

    public ReqMandateControllerTest() {
        MockitoAnnotations.openMocks(this);
    }

    @Test
    public void testCreateReqMandate() throws Exception {
        String custRef = "12345";
        ReqMandate reqMandate = new ReqMandate();
        reqMandate.getTxn().setId("txn123");
        
        when(reqMandateService.createReqMandate(custRef)).thenReturn(reqMandate);
        
        String expectedResponse = "<response>Success</response>";
        String upiSwitchUrl = "http://localhost:8081/upi/ReqMandate/2.0/urn:txnid:txn123";
        
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_XML);
        HttpEntity<String> entity = new HttpEntity<>("<reqMandate></reqMandate>", headers);
        
        when(restTemplate.postForEntity(upiSwitchUrl, entity, String.class)).thenReturn(ResponseEntity.ok(expectedResponse));
        
        String actualResponse = reqMandateController.createReqMandate(custRef);
        
        assertEquals(expectedResponse, actualResponse);
        verify(reqMandateService, times(1)).createReqMandate(custRef);
        verify(restTemplate, times(1)).postForEntity(upiSwitchUrl, entity, String.class);
    }
}