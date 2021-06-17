# Netscaler_Routine_Task_Automation
The script is written to automate NetScaler operational task like CSR creation, cert binding, bind/unbind and enable/disable real servers, publish/remove maintenance pages on vip, get details of the vip. The script will run the ip address of the vip through all th enetscaler ip addresses you provide in the netscale inventory csv file.

Below task are provided as option by the script. 

*************************************************************************
        The Netscaler Script can help perform below tasks
*************************************************************************



Press 1 to check the VIP details

Press 2 to publish the sorry page with RESPONDER-POLICY on the VIP - Python-API-Test-LbVServer
Press 3 to remove the sorry page with RESPONDER-POLICY on the VIP - Python-API-Test-LbVServer

Press 4 to publish the sorry page with REDIRECT-URL on the VIP - Python-API-Test-LbVServer
Press 5 to remove the sorry page with REDIRECT-URL on the VIP  - Python-API-Test-LbVServer

Press 6 to create Certificate Signing Request (CSR)

Press 7 to UPLOAD the certificate file received from the MWO team
Press 8 to create the Server CERT-KEY pair and link it to the CA CERT_KEY pair on the Netscaler

Press 9 to bind the Server CERT-KEY pair to the SSL vserver(VIP) on the Netscaler

Press 10 to BIND or UNBIND the Real Servers from the ServiceGroup on the Netscaler

Press 11 to ENABLE or DISABLE the Real Servers from the ServiceGroup on the Netscaler

Enter your Selection:
