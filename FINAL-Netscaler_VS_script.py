#!/usr/bin/python




# The below script provides details of vip hosted on  
# netscalers that are mentioned in the csv file

# Base file Created on: 18th April 2021
# Updated on: 11th May 2021

# Version-1: The version 1 included API calls for netscaler vip count
# Version-2: The version 2 included API calls for LBVSERVER details
#			 and LBVSERVER binding to SERVICEGROUP
# Version-3: The version 3 included API calls for LBVSERVER to CERTIFICATE binding,
#			 SERVICEGROUP to REAL server binding, exception handling when API calls 
#			 do not provide the correct list name or when API calls do not succeed
# Version-4: The version 4 included logic what to do when no SG, or no real server or no certificate binding
#			 is found, VIP to responder policy binding, responder policy details, responder policy to responder action binding details,
# Version-5: The version 5 included API call for responder action details, monitor binding details
# Version-6: The version 6 included API call for csverserv and related details
# Version-7: The version 7 changed the entire code to include functions
# Version-8: The version 8 included the sorry page with redirection and responder policy functions, save config function
# Version-9: The version 9 included the RSA KEY and CSR create functions
# Version-10: The version 10 included the CSR Detail find functions, upload to FTP server, 
#			  upload the certificate received from MWO team to the Netscaler
# Version-11: The version 11 included disabling of the csr upload to ftp server 
#			  as the snip ip address was not reachable
# Version-12: The version 12 included the nsversion check to support SAN CSR creation,
#			  ammended the workflos of the function csr create to include the nsverion check
# Version-13: The version 13 included the function to create the server cert-key pair and 
#			  link it to the CA cert-key pair
# Version-14: The version 14 included the function to bind the SSL vserver to the Server CERT-KEY pair
# Version-15: ther version 15 included the check all the netscalers primary and secondary 
#			  and run the script only on the primary netscaler and not the secondary
# Version-16: Ther version 16 replaced the paramiko module with API call in the 
#			  Server CERT-KEY pair bind to the VIP function
# Version-17: The version 17 included the real server bind/unbind with ServiceGroup function
# Version-18: The version 18 included the real server enable/disable within ServiceGroup function
# Version-19: The version 19 included the SSL VPN(VDI) VIP details module
# Version-20: The version 20 included the Authentication vserver VIP details module
# Version-21: The version 21 disabled the LB VIP count function





import sys
import os
import shutil
import time
import datetime
import socket
import ftplib
import csv
import re
import requests



username = 'ENTER_USERNAME_HERE'
password = 'ENTER_PASSWORD_HERE'


VIP_IP = ''
script_log = ''




def FUNC_VIP_COUNT_FIND(lb_name, lb_ip, VIP_IP):
	
	VIP_count = 0
	
	url10 = "http://" + str(lb_ip) + "/nitro/v1/config/lbvserver?count=yes"

	payload10  = {}

	try:
		response10 = requests.request("GET", url10, auth=(username, password), data = payload10)
		json_data10 = response10.json()
	except:
		print("The VIP count could not be determined from the LB")
		
	
	if 'lbvserver' in json_data10:
		VIP_count = json_data10['lbvserver'][0]['__count']
		print ("The number of VIP's in the Load balancer " + str(lb_name) + " with ip " + str(lb_ip) + " are: " + str(VIP_count))
		print ("Checking if the VIP " + str(VIP_IP) + " exists on the netscaler " + str(lb_name))		
	else:
		print("The API call did not provide the LBvserver List holding the VIP Count.")
		
	return VIP_count



def FUNC_LB_VIP_FIND(lb_name, lb_ip, VIP_IP):
	
	LB_VIP_NAME_LIST = []
	LB_VIP_NAME_DICT = {}
	LB_VIP_found = 0

	url20 = "http://" + str(lb_ip) + "/nitro/v1/config/lbvserver"

	payload20  = {}

	
	try:
		response20 = requests.request("GET", url20, auth=(username, password), data = payload20)
		json_data20 = response20.json()
	except:
		print("The Netscaler did not repsond to the API call")	

	if 'lbvserver' in json_data20:
		for i in json_data20['lbvserver']:
			if i['ipv46'] == VIP_IP:
				#print("The VIP " + VIP_IP + " exists in the LB Configuration of the LB: " + lb_name + " " + lb_ip)
				#print("The VIP name is: " + i['name'])
				LB_VIP_NAME_LIST.append(i['name'])
				LB_VIP_found = 1
	#else:
		#print("The API call did not provide the lbvserver list")
		
		
	if LB_VIP_found == 0:
		print("The VIP does not exists in the LB VIP configuration of the LB")
	

	return LB_VIP_NAME_LIST



def FUNC_LB_VIP_DETAILS_FIND(lb_name, lb_ip, VIP_IP, LB_VIP_NAME_LIST):

	for i in LB_VIP_NAME_LIST:
		url20 = "http://" + str(lb_ip) + "/nitro/v1/config/lbvserver?filter=name:" + str(i)

		payload20  = {}

		try:
			response20 = requests.request("GET", url20, auth=(username, password), data = payload20)
			json_data20 = response20.json()
		except:
			print("The Netscaler did not repsond to the API call")	
			
		
		if 'lbvserver' in json_data20:
			
			for x in json_data20['lbvserver']:
				
				print("\n**************************************************************************************************************")
				print("The LB VIP name is: " + str(x['name']) + " and the status is: " + str(x['curstate']))
				print("The LB VIP type is: " + str(x['servicetype']) + " and the port is: " + str(x['port']))
				print("The LB VIP last state change was on: " + str(x['statechangetimesec']))
				print("The Total configured real servers behind the VIP are : " + str(x['totalservices']) + " and active real servers are: " + str(x['activeservices']))
				print("The LB VIP loadbalancing method is: " + str(x['lbmethod']) + " and the client connection idle timeout(in seconds) is: " + str(x['clttimeout']))
				print("The LB VIP session persistence type is: " + str(x['persistencetype']) + " and the persistence timeout(in minutes) is: " + str(x['timeout']))
								
				if "redirurl" in x:
					print("The LB VIP if DOWN will redirect the connections to the URL as part of protection settings: " + str(x['redirurl']))
				else:
					print("The LB VIP is not configured to redirect connections if the VIP is DOWN as part of protection settings.")
				
				print("**************************************************************************************************************")
				
				FUNC_LB_VIP_CERT_BIND_FIND(lb_name, lb_ip, VIP_IP, x['name'])
				FUNC_LB_VIP_RESPONDERPOLICY_BIND_FIND(lb_name, lb_ip, VIP_IP, x['name'])
				FUNC_LB_VIP_SG_BIND_FIND(lb_name, lb_ip, VIP_IP, x['name'])
				
		else:
			print("The API call did not provide the lbvserver list")
	
	return



def FUNC_LB_VIP_SG_BIND_FIND(lb_name, lb_ip, VIP_IP, LB_VIP_NAME):

	LB_SG_NAME_LIST = []
	LB_SG_found = 0

	url20 = "http://" + str(lb_ip) + "/nitro/v1/config/lbvserver_servicegroup_binding?bulkbindings=yes"

	payload20  = {}

	try:
		response20 = requests.request("GET", url20, auth=(username, password), data = payload20)
		json_data20 = response20.json()
	except:
		print("The Netscaler did not repsond to the API call")	

	if 'lbvserver_servicegroup_binding' in json_data20:
		for x in json_data20['lbvserver_servicegroup_binding']:

			if str(LB_VIP_NAME) == x['name']:
				print("\nThe ServiceGroup binded to the VIP is: " + str(x['servicegroupname']))
				LB_SG_NAME_LIST.append(x['servicegroupname'])
				LB_SG_found = 1
				
				FUNC_LB_SG_DETAILS_FIND(lb_name, lb_ip, VIP_IP, x['servicegroupname'])
				FUNC_LB_SG_SRVR_BIND_FIND(lb_name, lb_ip, VIP_IP, x['servicegroupname'])
	else:
		print("The API call did not provide the lbvserver_servicegroup_binding list")
		
		
	if LB_SG_found == 0:
		print("")
		print("There is no ServiceGroup binded to the VIP.")
	
		FUNC_LB_VIP_SERVICE_BIND_FIND(lb_name, lb_ip, VIP_IP, LB_VIP_NAME)

	return 



def FUNC_LB_SG_DETAILS_FIND(lb_name, lb_ip, VIP_IP, LB_SG_NAME):
	
	url20 = "http://" + str(lb_ip) + "/nitro/v1/config/servicegroup?filter=servicegroupname:" + str(LB_SG_NAME)

	payload20  = {}

	try:
		response20 = requests.request("GET", url20, auth=(username, password), data = payload20)
		json_data20 = response20.json()
	except:
		print("The Netscaler did not repsond to the API call")	
		
	
	if 'servicegroup' in json_data20:
		
		for x in json_data20['servicegroup']:
			
			print("The Servicegroup name is: " + str(x['servicegroupname']) + " and the SG status is: " + str(x['servicegroupeffectivestate']))
			print("The Servicegroup type is: " + str(x['servicetype']) + " and the last status change of SG was on: " + str(x['statechangetimesec']) + "\n")
						
	else:
		print("The API call did not provide the lbvserver list")

	
	return



def FUNC_LB_SG_SRVR_BIND_FIND(lb_name, lb_ip, VIP_IP, LB_SG_NAME):

	url40 = "http://" + str(lb_ip) + "/nitro/v1/config/servicegroup_binding?bulkbindings=yes"

	payload40  = {}

	response40 = requests.request("GET", url40, auth=(username, password), data = payload40)
	json_data40 = response40.json()

	LB_SRVR_found = 0
	if 'servicegroup_binding' in json_data40:
		for y in json_data40['servicegroup_binding']:
			if y['servicegroupname'] == str(LB_SG_NAME):
				
				for z in y['servicegroup_servicegroupmember_binding']:
					if z['servicegroupname'] == str(LB_SG_NAME):
						
						print("The real server ip in the SG is: " + str(z['ip']) + " and the Status is: " + str(z['svrstate']))
						print("The real server port number is: " + str(z['port']) + " and the last status change of the real server was on: " + str(z['statechangetimesec']))
						LB_SRVR_found = 1
											
				print("")
				LB_Monitor_Found = 0
				if 'servicegroup_lbmonitor_binding' in y:
					for y2 in y['servicegroup_lbmonitor_binding']:
						if y2['servicegroupname'] == str(LB_SG_NAME):
							
							print("The Monitor name binded to the SG is: " + str(y2['monitor_name']) + " and the Status is: " + str(y2['state']))
							#print("The Monitor last response was: " + str(y2['lastresponse']))
							LB_Monitor_Found = 1
					
				if LB_Monitor_Found == 0:
					print("There is no Monitor binded to the ServiceGroup.")
					
	else:
		print("The API call did not provide the servicegroup_binding list")				

	
	if LB_SRVR_found == 0:
		print("There is no Real Server binded to the ServiceGroup.")

		
	return



def FUNC_LB_VIP_SERVICE_BIND_FIND(lb_name, lb_ip, VIP_IP, LB_VIP_NAME):

	url60 = "http://" + str(lb_ip) + "/nitro/v1/config/lbvserver_service_binding?bulkbindings=yes"

	payload60  = {}

	response60 = requests.request("GET", url60, auth=(username, password), data = payload60)
	json_data60 = response60.json()		

	if 'lbvserver_service_binding' in json_data60:
		LB_VIP_SERVICE_BIND_found = 0
		for d in json_data60['lbvserver_service_binding']:
			if d['name'] == str(LB_VIP_NAME):
				print("")
				print("The name of the Service bound to the VIP is: " + str(d['servicename']))
				print("The Service ip is: " + str(d['ipv46']) + " and the status is: " + str(d['curstate']))
				print("The Service type is: " + str(d['servicetype']) + " and the port is: " + str(d['port']))
				LB_VIP_SERVICE_BIND_found = 1
				
		if LB_VIP_SERVICE_BIND_found == 0:
				print ("\nThere is no Service binded directly to the VIP.")
				
	else:
		print("The API call did not provide the lbvserver_service_binding list")			
				
	return



def FUNC_LB_VIP_CERT_BIND_FIND(lb_name, lb_ip, VIP_IP, LB_VIP_NAME):

	url50 = "http://" + str(lb_ip) + "/nitro/v1/config/sslvserver_binding?bulkbindings=yes"

	payload50  = {}

	response50 = requests.request("GET", url50, auth=(username, password), data = payload50)
	json_data50 = response50.json()
	
	
	if 'sslvserver_binding' in json_data50:
		LB_CERT_found = 0
		for g in json_data50['sslvserver_binding']:
			if g['vservername'] == str(LB_VIP_NAME):
				
				for g1 in g['sslvserver_sslcertkey_binding']:

					print("\nThe CERT-KEY pair name binded to the VIP is: " + str(g1['certkeyname']))
					LB_CERT_found = 1
					
					FUNC_LB_VIP_CERT_DETAILS_FIND(lb_name, lb_ip, VIP_IP, g1['certkeyname'])
		
		if LB_CERT_found == 0:
			print("")
			print("There is no CERT-KEY pair binded to the VIP.")	
			
	else:
		print("The API call did not provide the sslvserver_binding list")

		
	return



def FUNC_LB_VIP_CERT_DETAILS_FIND(lb_name, lb_ip, VIP_IP, LB_VIP_CERTKEY_NAME):


	url51 = "http://" + str(lb_ip) + "/nitro/v1/config/sslcertkey?filter=certkey:" + str(LB_VIP_CERTKEY_NAME)

	payload51  = {}

	response51 = requests.request("GET", url51, auth=(username, password), data = payload51)
	json_data51 = response51.json()

	if 'sslcertkey' in json_data51:
		
		for g2 in json_data51['sslcertkey']:
		
			print("The certificate details are: ")
			print("Certificate Status: " + str(g2['status']))
			print("Certificate Serial no.: " + str(g2['serial']))
			print("Certificate type is: " + str(g2['certificatetype']))
			print("Issuer: " + str(g2['issuer']))
			print("Issue Date: " + str(g2['clientcertnotbefore']))
			print("Expiry Date: " + str(g2['clientcertnotafter']))
			print("No. of days to Expire: " + str(g2['daystoexpiration']))
	else:
		print("The API call did not provide the sslcertkey list")
		
		
	return



def FUNC_LB_VIP_RESPONDERPOLICY_BIND_FIND(lb_name, lb_ip, VIP_IP, LB_VIP_NAME):

	url70 = "http://" + str(lb_ip) + "/nitro/v1/config/responderpolicy_lbvserver_binding?bulkbindings=yes"

	payload70  = {}

	response70 = requests.request("GET", url70, auth=(username, password), data = payload70)
	json_data70 = response70.json()

	if 'responderpolicy_lbvserver_binding' in json_data70:
		LB_RESPONDERPOLICY_found = 0
		for r in json_data70['responderpolicy_lbvserver_binding']:
			
			if LB_VIP_NAME in r['boundto']:
				print("")
				print("The ResponderPolicy name binded to the VIP is: " + str(r['name']))
				print("The ResponderPolicy priority is: " + str(r['priority']))
				LB_RESPONDERPOLICY_found = 1
				
				FUNC_LB_VIP_RESPONDERPOLICY_DETAILS_FIND(lb_name, lb_ip, VIP_IP, r['name'])
				
		if LB_RESPONDERPOLICY_found == 0:
			print("\nThere is no ResponderPolicy binded to the VIP.")
			
	else:
		print("The API call did not provide the responderpolicy_lbvserver_binding list")

	return



def FUNC_LB_VIP_RESPONDERPOLICY_DETAILS_FIND(lb_name, lb_ip, VIP_IP, LB_RESPONDERPOLICY_NAME):

	url71 = "http://" + str(lb_ip) + "/nitro/v1/config/responderpolicy"

	payload71  = {}

	response71 = requests.request("GET", url71, auth=(username, password), data = payload71)
	json_data71 = response71.json()								

	if 'responderpolicy' in json_data71:
		LB_RESPONDERPOLICY_DETAILS_found = 0
		for r2 in json_data71['responderpolicy']:
			
			if r2['name'] == LB_RESPONDERPOLICY_NAME:
				print("The ResponderPolicy rule is: " + str(r2['rule']))
				if r2['action'] == "NOOP" or r2['action'] == "RESET" or r2['action'] == "DROP":
					print("\nThe ResponderAction binded to the ResponderPolicy is: " + str(r2['action']))
					LB_RESPONDERPOLICY_DETAILS_found = 1
				else:
					print("\nThe ResponderAction binded to the ResponderPolicy is: " + str(r2['action']))
					LB_RESPONDERPOLICY_DETAILS_found = 1
					
					FUNC_LB_VIP_RESPONDERACTION_DETAILS_FIND(lb_name, lb_ip, VIP_IP, r2['action'])
							
		if LB_RESPONDERPOLICY_DETAILS_found == 0:
			print("\nThe ResponderPolicy details could not be fetched from the Netscaler.")
	else:
		print("The API call did not provide the responderpolicy list")

	return



def FUNC_LB_VIP_RESPONDERACTION_DETAILS_FIND(lb_name, lb_ip, VIP_IP, LB_RESPONDERACTION_NAME):

	url72 = "http://" + str(lb_ip) + "/nitro/v1/config/responderaction"

	payload72  = {}

	response72 = requests.request("GET", url72, auth=(username, password), data = payload72)
	json_data72 = response72.json()	
								
	if 'responderaction' in json_data72:
		LB_RESPONDERACTION_DETAILS_found = 0
		
		for r3 in json_data72['responderaction']:
			if r3['name'] == LB_RESPONDERACTION_NAME:
				#print("")
				print("The ResponderAction type is: " + str(r3['type']))
				print("The ResponderAction target is: " + str(r3['target']))
				LB_RESPONDERACTION_DETAILS_found = 1
				
		if LB_RESPONDERACTION_DETAILS_found == 0:
			print("\nThe ResponderAction details could not be fetched from the Netscaler.")							
	
	else:
		print("The API call did not provide the responderaction list")
		
		
	return



def FUNC_CS_VIP_FIND(lb_name, lb_ip, VIP_IP):
	
	CS_VIP_NAME_LIST = []
	CS_VIP_found = 0
	
	url30 = "http://" + str(lb_ip) + "/nitro/v1/config/csvserver"

	payload30  = {}

	
	try:
		response30 = requests.request("GET", url30, auth=(username, password), data = payload30)
		json_data30 = response30.json()
	except:
		print("The Netscaler did not repsond to the API call")
			
			
	if 'csvserver' in json_data30:		
		for i in json_data30['csvserver']:
			if i['ipv46'] == VIP_IP:
				#print("The VIP " + VIP_IP + " exists in the CS Configuration of the LB: " + lb_name + " " + lb_ip)
				#print("The VIP name is: " + i['name'])
				CS_VIP_NAME_LIST.append(i['name'])
				CS_VIP_found = 1
	#else:
		#print("The API call did not provide the csvserver list")
		
		
	if CS_VIP_found == 0:
		print("The VIP does not exists in the CS VIP configuration of the LB")	
	
	
	return CS_VIP_NAME_LIST



def FUNC_VDI_VIP_FIND(lb_name, lb_ip, VIP_IP):
	
	VDI_VIP_NAME_LIST = []
	VDI_VIP_found = 0
	
	url30 = "http://" + str(lb_ip) + "/nitro/v1/config/vpnvserver"

	payload30  = {}
	
	
	try:
		response30 = requests.request("GET", url30, auth=(username, password), data = payload30)
		json_data30 = response30.json()
	except:
		print("The Netscaler did not repsond to the API call")
			
			
	if 'vpnvserver' in json_data30:		
		for i in json_data30['vpnvserver']:
			if i['ipv46'] == VIP_IP:
				#print("The VIP " + VIP_IP + " exists in the SSL VPN(VDI) VIP Configuration of the LB: " + lb_name + " " + lb_ip)
				#print("The VIP name is: " + i['name'])
				VDI_VIP_NAME_LIST.append(i['name'])
				VDI_VIP_found = 1
				
	#else:
		#print("The API call did not provide the vpnvserver list")
		
		
	if VDI_VIP_found == 0:
		print("The VIP does not exists in the SSL VPN(VDI) VIP configuration of the LB")	
	
	
	return VDI_VIP_NAME_LIST




def FUNC_CS_VIP_DETAILS_FIND(lb_name, lb_ip, VIP_IP, CS_VIP_NAME_LIST):

	for i in CS_VIP_NAME_LIST:
	
		url30 = "http://" + str(lb_ip) + "/nitro/v1/config/csvserver?filter=name:" + str(i)

		payload30  = {}

		try:
			response30 = requests.request("GET", url30, auth=(username, password), data = payload30)
			json_data30 = response30.json()
		except:
			print("The Netscaler did not repsond to the API call")	
			
		
		if 'csvserver' in json_data30:
			
			for x in json_data30['csvserver']:
				
				print("\n**************************************************************************************************************")
				print("The CS VIP name is: " + str(x['name']) + " and the status is: " + str(x['curstate']))
				print("The CS VIP type is: " + str(x['servicetype']) + " and the port is: " + str(x['port']))
				print("The CS VIP last state change was on: " + str(x['statechangetimesec']))
				print("The CS VIP client connection idle timeout(in seconds) is: " + str(x['clttimeout']))

				if "redirurl" in x:
					print("The CS VIP if DOWN will redirect the connections to the URL as part of protection settings: " + str(x['redirurl']))
				else:
					print("The CS VIP is not configured to redirect connections if the VIP is DOWN as part of protection settings.")
				
				print("**************************************************************************************************************\n")
				
				FUNC_LB_VIP_CERT_BIND_FIND(lb_name, lb_ip, VIP_IP, x['name'])
				FUNC_CS_VIP_CSPOLICY_BIND_FIND(lb_name, lb_ip, VIP_IP, x['name'])
								
		else:
			print("The API call did not provide the csvserver list")
	
	return




def FUNC_VDI_VIP_DETAILS_FIND(lb_name, lb_ip, VIP_IP, VDI_VIP_NAME_LIST):

	for i in VDI_VIP_NAME_LIST:
	
		url30 = "http://" + str(lb_ip) + "/nitro/v1/config/vpnvserver?filter=name:" + str(i)

		payload30  = {}

		try:
			response30 = requests.request("GET", url30, auth=(username, password), data = payload30)
			json_data30 = response30.json()
		except:
			print("The Netscaler did not repsond to the API call to fetch the SSL VPN(VDI) VIP details.")	
			
		
		if 'vpnvserver' in json_data30:
			
			for x in json_data30['vpnvserver']:
				
				print("\n**************************************************************************************************************")
				print("The SSL VPN(VDI) VIP name is: " + str(x['name']) + " and the status is: " + str(x['curstate']))
				print("The SSL VPN(VDI) VIP type is: " + str(x['servicetype']) + " and the port is: " + str(x['port']))
				if "vserverfqdn" in x:
					print("The SSL VPN(VDI) VIP fqdn is: " + str(x['vserverfqdn']) + " and the ip is: " + str(x['ipv46']) )
				else:
					print("The SSL VPN(VDI) VIP ip address is: " + str(x['ipv46']) )
				print("**************************************************************************************************************\n")
				
				FUNC_LB_VIP_CERT_BIND_FIND(lb_name, lb_ip, VIP_IP, x['name'])
				#FUNC_CS_VIP_CSPOLICY_BIND_FIND(lb_name, lb_ip, VIP_IP, x['name'])
								


				url40 = "http://" + str(lb_ip) + "/nitro/v1/config/vpnvserver_binding/" + str(i)

				payload40  = {}

				try:
					response40 = requests.request("GET", url40, auth=(username, password), data = payload40)
					json_data40 = response40.json()
				except:
					print("The Netscaler did not repsond to the API call to fetch the SSL VPN(VDI) VIP Binding details.")
					

				if 'vpnvserver_binding' in json_data40:
					
					for y in json_data40['vpnvserver_binding']:
					
						if 'vpnvserver_vpnsessionpolicy_binding' in y:
							
							for y1 in y['vpnvserver_vpnsessionpolicy_binding']:
								
								print("")
								print("The SessionPolicy name binded to the SSL VPN(VDI) VIP is: " + y1['policy'])
								print("The SessionPolicy priority is: " + y1['priority'])
								
								
								
								url50 = "http://" + str(lb_ip) + "/nitro/v1/config/vpnsessionpolicy/" + str(y1['policy'])

								payload50  = {}								
								
								response50 = requests.request("GET", url50, auth=(username, password), data = payload50)
								json_data50 = response50.json()		

								if 'vpnsessionpolicy' in json_data50:
									
									for z1 in json_data50['vpnsessionpolicy']:
									
										print("The SessionPolicy rule is: " + z1['rule'])
										#print("")
										print("The SessionPolicy action is: " + z1['action'])
								


										url60 = "http://" + str(lb_ip) + "/nitro/v1/config/vpnsessionaction/" + str(z1['action'])

										payload60  = {}								
										
										response60 = requests.request("GET", url60, auth=(username, password), data = payload60)
										json_data60 = response60.json()		

										if 'vpnsessionaction' in json_data60:
											
											for z2 in json_data60['vpnsessionaction']:
											
												print("The SessionPolicy action defaultauthorizationaction is: " + z2['defaultauthorizationaction'])
												print("The SessionPolicy action icaproxy is: " + z2['icaproxy'])
												print("The SessionPolicy action wihome URL is: " + z2['wihome'])
								

										else:
											
											print("The API call did not provide the vpnsessionaction list ")
								
								else:
									
									print("The API call did not provide the vpnsessionpolicy list ")																
							
						else:
							
							print("The API call did not provide the vpnvserver_vpnsessionpolicy_binding list ")



						if 'vpnvserver_authenticationradiuspolicy_binding' in y:
							
							for y2 in y['vpnvserver_authenticationradiuspolicy_binding']:
								
								print("")
								print("The AuthenticationRadiusPolicy name binded to the SSL VPN(VDI) VIP is: " + y2['policy'])
								print("The AuthenticationRadiusPolicy priority is: " + y2['priority'])




								url50 = "http://" + str(lb_ip) + "/nitro/v1/config/authenticationradiuspolicy/" + str(y2['policy'])

								payload50  = {}								
								
								response50 = requests.request("GET", url50, auth=(username, password), data = payload50)
								json_data50 = response50.json()		

								if 'authenticationradiuspolicy' in json_data50:
									
									for z1 in json_data50['authenticationradiuspolicy']:
									
										print("The AuthenticationRadius Policy rule is: " + z1['rule'])
										#print("")
										print("The AuthenticationRadius Policy action is: " + z1['reqaction'])
								


										url60 = "http://" + str(lb_ip) + "/nitro/v1/config/authenticationradiusaction/" + str(z1['reqaction'])

										payload60  = {}								
										
										response60 = requests.request("GET", url60, auth=(username, password), data = payload60)
										json_data60 = response60.json()		

										if 'authenticationradiusaction' in json_data60:
											
											for z2 in json_data60['authenticationradiusaction']:
											
												print("The AuthenticationRadius action server ip is: " + z2['serverip'])
												print("The AuthenticationRadius action server port is: " + str(z2['serverport']))
												print("The AuthenticationRadius action radkey is: " + z2['radkey'])
								

										else:
											
											print("The API call did not provide the authenticationradiusaction list ")

									
									
								else:
									print("The API call did not provide the authenticationradiuspolicy list ")















							
							
						else:
							
							print("The API call did not provide the vpnvserver_authenticationradiuspolicy_binding list ")



						if 'vpnvserver_vpnportaltheme_binding' in y:
							
							for y3 in y['vpnvserver_vpnportaltheme_binding']:
								
								print("")
								print("The Portal Theme name binded to the SSL VPN(VDI) VIP is: " + y3['portaltheme'])
							
							
						else:
							
							print("The API call did not provide the vpnvserver_vpnportaltheme_binding list ")



						if 'vpnvserver_staserver_binding' in y:
							
							for y4 in y['vpnvserver_staserver_binding']:
								print("")
								print("The StoreFront Server URL is: " + y4['staserver'])
								#print("The StoreFront Server auth-id is: " + y4['staauthid'])
								
								if 'stastate' in y4:
									print("The StoreFront Server state is: " + y4['stastate'])
								
								else:
									if 'stateflag' in y4:
										if y4['stateflag'] == '536938508':
											print("The StoreFront Server state is UP.")
										else:
											print("The StoreFront Server state is DOWN.")
													
						else:
							
							print("The API call did not provide the vpnvserver_staserver_binding list ")
			
				else:
					print("The API call did not provide the vpnvserver_binding list")
						
								
		else:
			print("The API call did not provide the vpnvserver list")
	
	return




def FUNC_AUTH_VIP_FIND(lb_name, lb_ip, VIP_IP):
	
	AUTH_VIP_NAME_LIST = []
	AUTH_VIP_NAME_DICT = {}
	AUTH_VIP_found = 0

	url20 = "http://" + str(lb_ip) + "/nitro/v1/config/authenticationvserver"

	payload20  = {}

	
	try:
		response20 = requests.request("GET", url20, auth=(username, password), data = payload20)
		json_data20 = response20.json()
	except:
		print("The Netscaler did not repsond to the API call")	

	if 'authenticationvserver' in json_data20:
		for i in json_data20['authenticationvserver']:
			if i['ipv46'] == VIP_IP:
				#print("The VIP " + VIP_IP + " exists in the Authentication vserver Configuration of the LB: " + lb_name + " " + lb_ip)
				#print("The VIP name is: " + i['name'])
				AUTH_VIP_NAME_LIST.append(i['name'])
				AUTH_VIP_found = 1
	#else:
		#print("The API call did not provide the authenticationvserver list")
		
		
	if AUTH_VIP_found == 0:
		print("The VIP does not exists in the Authentication vserver VIP configuration of the LB")
	

	return AUTH_VIP_NAME_LIST




def FUNC_CS_VIP_CSPOLICY_BIND_FIND(lb_name, lb_ip, VIP_IP, CS_VIP_NAME):


	url130 = "http://" + str(lb_ip) + "/nitro/v1/config/csvserver_binding?bulkbindings=yes"

	payload130  = {}

	response130 = requests.request("GET", url130, auth=(username, password), data = payload130)
	json_data130 = response130.json()

	if 'csvserver_binding' in json_data130:
		
		CS_VIP_CSPOLICY_found = 0
		
		for g in json_data130['csvserver_binding']:
			if g['name'] == CS_VIP_NAME:
				
				if 'csvserver_cspolicy_binding' in g:
					
					for g1 in g['csvserver_cspolicy_binding']:

						print("\nThe CS Policy name binded to the CS VIP is: " + str(g1['policyname']))
						print("The CS Policy priority is: " + str(g1['priority']))
						CS_VIP_CSPOLICY_found = 1
						
						FUNC_CS_VIP_CSPOLICY_DETAILS_FIND(lb_name, lb_ip, VIP_IP, g1['policyname'])
						
				
				else:
					print("The API call did not provide the csvserver_cspolicy_binding list")
					
				
				if 'csvserver_responderpolicy_binding' in g:
					
					CS_VIP_RESPONDERPOLICY_found = 0
					for g11 in g['csvserver_responderpolicy_binding']:
					
						if g11['name'] == CS_VIP_NAME:
							print("\nThe CS ResponderPolicy name binded to the CS VIP is: " + str(g11['policyname']))
							print("The CS ResponderPolicy priority is: " + str(g11['priority']))
							CS_VIP_RESPONDERPOLICY_found = 1
							
							FUNC_LB_VIP_RESPONDERPOLICY_DETAILS_FIND(lb_name, lb_ip, VIP_IP, g11['policyname'])							
				
				else:
					print("The API call did not provide the csvserver_responderpolicy_binding list")
		
		if CS_VIP_CSPOLICY_found == 0:
			print("\nThere is no CS Policy binded to the CS VIP.")
		elif CS_VIP_RESPONDERPOLICY_found == 0:
			print("\nThere is no CS ResponderPolicy binded to the CS VIP.")
		
	else:
		print("The API call did not provide the csvserver_binding list")
		
		
		
	return



def FUNC_CS_VIP_CSPOLICY_DETAILS_FIND(lb_name, lb_ip, VIP_IP, CSPOLICY_NAME):

	url131 = "http://" + str(lb_ip) + "/nitro/v1/config/cspolicy"

	payload131  = {}

	response131 = requests.request("GET", url131, auth=(username, password), data = payload131)
	json_data131 = response131.json()
	
	
	if 'cspolicy' in json_data131:
		
		CS_VIP_CSPOLICY_DETALS_found = 0
		for g2 in json_data131['cspolicy']:

			if g2['policyname'] == CSPOLICY_NAME:	
				print("The CS policy rule is: " + str(g2['rule']))
				print("The CS Action binded to the CS policy rule is:: " + str(g2['action']))
				CS_VIP_CSPOLICY_DETALS_found = 1
				
				FUNC_CS_VIP_CSPOLICY_CSACTION_BIND_FIND(lb_name, lb_ip, VIP_IP, g2['action'])

		if CS_VIP_CSPOLICY_DETALS_found == 0:
			print("\nThe CS Policy details could not be found.")									
	else:
		print("The API call did not provide the cspolicy list")	
	
	return



def FUNC_CS_VIP_CSPOLICY_CSACTION_BIND_FIND(lb_name, lb_ip, VIP_IP, CSACTION_NAME):

	url132 = "http://" + str(lb_ip) + "/nitro/v1/config/csaction"

	payload132  = {}

	response132 = requests.request("GET", url132, auth=(username, password), data = payload132)
	json_data132 = response132.json()
	
	if 'csaction' in json_data132:
		CS_VIP_CSPOLICY_CSACTION_found = 0
		for g3 in json_data132['csaction']:
		
			if g3['name'] == CSACTION_NAME:

				if 'targetlbvserver' in g3:
					print("The CS Action Target LB VIP is: " + str(g3['targetlbvserver']))
					
#					FUNC_CS_VIP_BIND_LB_VIP_DETAILS_FIND(lb_name, lb_ip, VIP_IP, g3['targetlbvserver'])
					
				elif 'targetvserverexpr' in g3:
					print("The CS Action Target Expression is: " + str(g3['targetvserverexpr']))
				
				CS_VIP_CSPOLICY_CSACTION_found = 1	
	
		if CS_VIP_CSPOLICY_CSACTION_found == 0:
			print("\nThe CS Action details could not be found.")									
	else:
		print("The API call did not provide the csaction list")	
		
	return



def FUNC_CS_VIP_BIND_LB_VIP_DETAILS_FIND(lb_name, lb_ip, VIP_IP, LB_VIP_NAME):


	url20 = "http://" + str(lb_ip) + "/nitro/v1/config/lbvserver?filter=name:" + str(LB_VIP_NAME)

	payload20  = {}

	try:
		response20 = requests.request("GET", url20, auth=(username, password), data = payload20)
		json_data20 = response20.json()
	except:
		print("The Netscaler did not repsond to the API call")	
		
	
	if 'lbvserver' in json_data20:
		
		for x in json_data20['lbvserver']:
			
			print("\n**************************************************************************************************************")
			print("The LB VIP name is: " + str(x['name']) + " and the status is: " + str(x['curstate']))
			print("The LB VIP type is: " + str(x['servicetype']) + " and the port is: " + str(x['port']))
			print("The LB VIP last state change was on: " + str(x['statechangetimesec']))
			print("The Total configured real servers behind the VIP are : " + str(x['totalservices']) + " and active real servers are: " + str(x['activeservices']))
			print("The LB VIP loadbalancing method is: " + str(x['lbmethod']) + " and the client connection idle timeout(in seconds) is: " + str(x['clttimeout']))
			print("The LB VIP session persistence type is: " + str(x['persistencetype']) + " and the persistence timeout(in minutes) is: " + str(x['timeout']))
							
			if "redirurl" in x:
				print("The LB VIP if DOWN will redirect the connections to the URL as part of protection settings: " + str(x['redirurl']))
			else:
				print("The LB VIP is not configured to redirect connections if the VIP is DOWN as part of protection settings.")
			
			print("**************************************************************************************************************")
			
			FUNC_LB_VIP_CERT_BIND_FIND(lb_name, lb_ip, VIP_IP, x['name'])
			FUNC_LB_VIP_RESPONDERPOLICY_BIND_FIND(lb_name, lb_ip, VIP_IP, x['name'])
			FUNC_LB_VIP_SG_BIND_FIND(lb_name, lb_ip, VIP_IP, x['name'])
			
	else:
		print("The API call did not provide the lbvserver list")

	return



def FUNC_CHECK_NETSCALER_PRI_OR_SEC_IN_HA(lb_ip):


	url = "http://" + str(lb_ip) + "/nitro/v1/config/hanode"

	payload  = {}

	response = requests.request("GET", url, auth=(username, password), data = payload)
	json_data = response.json()

	
	if 'hanode' in json_data:
		
		for x in json_data['hanode']:
		
			if x['state'] == 'PRIMARY' or x['state'] == 'Primary':
			
				pri_lb_ip = x['ipaddress']
				
			elif x['state'] == 'SECONDARY' or x['state'] == 'Secondary':
				
				sec_lb_ip = x['ipaddress']
		
	else:
		
		print("")
		print("The API call could not provide the hanode list to find the HA Status of the Netscaler.")
		
		


	if lb_ip == pri_lb_ip:
		print("")
		print("\n\nThe provided Netscaler ip address: " + lb_ip + " is the Primary Netscaler in the HA node.")
		FUNC_lb_ip = pri_lb_ip

	elif lb_ip == sec_lb_ip:
		print("")
		print("\n\nThe provided Netscaler ip address: " + lb_ip + " is the Secondary Netscaler in the HA node.")
		print("The Netscaler ip address will be changed to the Primary Netscaler ip address: " + pri_lb_ip)
		FUNC_lb_ip = pri_lb_ip
	


	
	return FUNC_lb_ip



def FUNC_VIP_START():

	username = 'ENTER_USERNAME_HERE'
	password = 'ENTER_PASSWORD_HERE'
	VIP_IP = ''
	
	VIP_IP = input("Enter the ip address of the VIP: ")
	#script_log = "\n" + script_log + VIP_IP 

	netscaler_ip_file = "netscaler_ip_details.csv"

	with open (netscaler_ip_file) as netscaler_ip_csvfile:
	# Creating a CSV reader
		netscaler_ip_csvreader = csv.reader(netscaler_ip_csvfile)
		
		for row in netscaler_ip_csvreader:
		
	# Saving the vaule of the Netscaler device name and tripping whitespaces
			lb_name = row[0].strip()

	# Saving the vaule of the Netscaler device name and tripping whitespaces
			lb_ip = row[2].strip()

			
	#Check for Primary or Secondary node 
			url = "http://" + str(lb_ip) + "/nitro/v1/config/hanode"

			payload  = {}
			
			try:
				
				response = requests.request("GET", url, auth=(username, password), data = payload, timeout=30)
				json_data = response.json()

			except:
				
				print("\n\n\n\n")
				print("The Netscaler: " + str(lb_name) + " - " + str(lb_ip) + " is not responding to API Call.")
				print("Please check if the Netscaler is UP and accessible on HTTP port for API call.")
				print("\n\n")

			else:
				
				if 'hanode' in json_data:
					
					for x in json_data['hanode']:
					
						if x['state'] == 'PRIMARY' or x['state'] == 'Primary':
						
							pri_lb_ip = x['ipaddress']
							
						elif x['state'] == 'SECONDARY' or x['state'] == 'Secondary':
							
							sec_lb_ip = x['ipaddress']
					
				else:
					
					print("")
					print("The API call could not provide the hanode list to find the HA Status of the Netscaler.")
					
					

				print ("\n\nChecking if the VIP " + str(VIP_IP) + " exists on the netscaler " + str(lb_name))

				
				if lb_ip == pri_lb_ip:
					#print("")				
					print("The provided Netscaler ip address: " + lb_ip + " is the Primary Netscaler in the HA node.")				
					TEMP_lb_ip = pri_lb_ip




			################################################################################################################		
			# Count the number of VIP's in Load balancer 
					#VIP_count = 0		
					#VIP_count = FUNC_VIP_COUNT_FIND(lb_name, lb_ip, VIP_IP)



			################################################################################################################
			#  GET the Authentication VIP vserver details from the netscaler LB 
					
					MAIN_AUTH_VIP_NAME_LIST = []		
					MAIN_AUTH_VIP_NAME_LIST = FUNC_AUTH_VIP_FIND(lb_name, lb_ip, VIP_IP)



			################################################################################################################
			#  GET the SSL VPN (VDI) VIP vserver details from the netscaler LB 
					
					MAIN_VDI_VIP_NAME_LIST = []		
					MAIN_VDI_VIP_NAME_LIST = FUNC_VDI_VIP_FIND(lb_name, lb_ip, VIP_IP)



			################################################################################################################
			#  GET the LB VIP vserver details from the netscaler LB 

					MAIN_LB_VIP_NAME_LIST = []
					MAIN_LB_VIP_NAME_LIST = FUNC_LB_VIP_FIND(lb_name, lb_ip, VIP_IP)
				
				
				
			################################################################################################################
			#  GET the CS VIP vserver details from the netscaler LB 
					
					MAIN_CS_VIP_NAME_LIST = []		
					MAIN_CS_VIP_NAME_LIST = FUNC_CS_VIP_FIND(lb_name, lb_ip, VIP_IP)


					
			################################################################################################################
			# Check if VIP exists in Authentication VIP or SSL VPN(VDI) or LB or CS VIP configuration
					if MAIN_AUTH_VIP_NAME_LIST:
						#print("\nThe VIP is a Authentication vServer.")
						print("\nFound " + str(len(MAIN_AUTH_VIP_NAME_LIST)) + " VIP in the Authentication vServer VIP section")
						print("The Authentication VIP name is: ")
						print(MAIN_AUTH_VIP_NAME_LIST)
						print("Please reach out to the Network team for details of the VIP.")
						#print(MAIN_AUTH_VIP_NAME_LIST)

					if MAIN_VDI_VIP_NAME_LIST:
						#print("\nThe VIP is a SSL VPN(VDI) VIP.")
						print("\nFound " + str(len(MAIN_VDI_VIP_NAME_LIST)) + " VIP in the SSL VPN(VDI) VIP section")
						#print(MAIN_VDI_VIP_NAME_LIST)

					if MAIN_LB_VIP_NAME_LIST:
						#print("\nThe VIP is a LoadBalancing VIP.")
						print("\nFound " + str(len(MAIN_LB_VIP_NAME_LIST)) + " VIP in the LoadBalancing VIP section")
						#print(MAIN_LB_VIP_NAME_LIST)
					
					if MAIN_CS_VIP_NAME_LIST:
						#print("\nThe VIP is a Content Switching VIP.")
						print("\nFound " + str(len(MAIN_CS_VIP_NAME_LIST)) + " VIP in the ContentSwitching VIP section")
						#print(MAIN_CS_VIP_NAME_LIST)

					
					
					if MAIN_AUTH_VIP_NAME_LIST:
						print("")
					elif MAIN_VDI_VIP_NAME_LIST:
						print("")
					elif MAIN_LB_VIP_NAME_LIST:
						print("")
					elif MAIN_CS_VIP_NAME_LIST:
						print("")
					else:
						print("THE VIP WAS NOT FOUND ON THE NETSCALER.")

					
					
			################################################################################################################
			# Get the details of the SSL VPN(VDI) or LB & CS VIP

					if MAIN_VDI_VIP_NAME_LIST:
						FUNC_VDI_VIP_DETAILS_FIND(lb_name, lb_ip, VIP_IP, MAIN_VDI_VIP_NAME_LIST)

					if MAIN_LB_VIP_NAME_LIST:
						FUNC_LB_VIP_DETAILS_FIND(lb_name, lb_ip, VIP_IP, MAIN_LB_VIP_NAME_LIST)
					
					if MAIN_CS_VIP_NAME_LIST:
						FUNC_CS_VIP_DETAILS_FIND(lb_name, lb_ip, VIP_IP, MAIN_CS_VIP_NAME_LIST)




				elif lb_ip == sec_lb_ip:
					#print("")
					print("The provided Netscaler ip address: " + lb_ip + " is the Secondary Netscaler in the HA node.")
					print("The VIP check will only performed on the Primary Netscaler ip address: " + pri_lb_ip)

				
			

	return



def FUNC_SORRY_PAGE_PUBLISH_Python_API_Test_LbVServer():

	import requests
	import json

	username = 'ENTER_USERNAME_HERE'
	password = 'ENTER_PASSWORD_HERE'
	
##################################################################################################
################################## PUBLISHING SORRY PAGE #########################################
##################################################################################################
	
	print("")
	print("You have requested to Publish Sorry Page on the test VIP Python-API-Test-LbVServer.")
	PUBLISH_SORRY_PAGE = input("Are you Sure? Press [Y/N]: ")
	
	if PUBLISH_SORRY_PAGE == 'Y' or PUBLISH_SORRY_PAGE == 'y':
		print("")
		print("Publishing Sorry Page now!!")
		
		url = "http://ENTER_NETSCALER_IP_HERE/nitro/v1/config/lbvserver_responderpolicy_binding"

		payload = json.dumps({
		  "lbvserver_responderpolicy_binding": {
			"name": "Python-API-Test-LbVServer",
			"policyname": "pol-sorry-page",
			"priority": "100"
		  }
		})


		headers = {
				'Content-Type': 'application/json'
		}

		response = requests.request("POST", url, auth=(username, password), headers=headers, data=payload)

		
		if response.status_code in [200,201,202]:
			
			print("The Sorry Page was publised Successfully.")
			
			FUNC_SAVE_CONFIG("ENTER_NETSCALER_IP_HERE")
			
		else:
			print("The Sorry Page could not be published.")

	elif PUBLISH_SORRY_PAGE == 'N' or PUBLISH_SORRY_PAGE == 'n':
		
		print("The user requested not to Publish the SORRY page.")
	
	else:
		
		print("")
		print("The user provided an invalid input. The SORRY page will not be published.")
	
	
	
	return



def FUNC_SORRY_PAGE_REMOVE_Python_API_Test_LbVServer():

	import requests
	import json

	username = 'ENTER_USERNAME_HERE'
	password = 'ENTER_PASSWORD_HERE'
	
##################################################################################################
################################## REMOVE the  SORRY PAGE ########################################
##################################################################################################
	print("")
	print("You have requested to Remove the Sorry Page on the test VIP Python-API-Test-LbVServer.")
	REMOVE_SORRY_PAGE = input("Are you Sure? Press [Y/N]: ")
	
	if REMOVE_SORRY_PAGE == 'Y' or REMOVE_SORRY_PAGE == 'y':
	
	
		print("")
		print("Removing the Sorry Page now!!")
		
		url = "http://ENTER_NETSCALER_IP_HERE/nitro/v1/config/lbvserver_responderpolicy_binding/Python-API-Test-LbVServer?args=policyname:pol-sorry-page"

		payload = {}


		headers = {}

		response = requests.request("DELETE", url, auth=(username, password), headers=headers, data=payload)

		
		if response.status_code in [200,201,202]:
			
			print("The Sorry Page was removed Successfully.")
			
			FUNC_SAVE_CONFIG("ENTER_NETSCALER_IP_HERE")
		
		elif response.status_code == 599:	
			print("The Sorry Page could not be removed.")
			print("Cannot unbind a policy that is not bound.")

		else:
			print("The Sorry Page could not be removed.")

	elif REMOVE_SORRY_PAGE == 'N' or REMOVE_SORRY_PAGE == 'n':
		
		print("The user requested not to Remove the SORRY page.")
	
	else:
		
		print("")
		print("The user provided an invalid input. The SORRY page will not be removed.")
	
	
	
	
	return
	
	

def FUNC_REDIRECT_URL_CONFIGURE_Python_API_Test_LbVServer():


	import requests
	import json

	username = 'ENTER_USERNAME_HERE'
	password = 'ENTER_PASSWORD_HERE'
	
	DISABLE_VIP = 0
	ADD_REDIRECT_URL = 0
	
##################################################################################################
################################## CONFIGURE REDIRECT-URL ########################################
##################################################################################################

	print("")
	print("You have requested to Publish Sorry Page on the test VIP Python-API-Test-LbVServer.")
	PUBLISH_SORRY_PAGE = input("Are you Sure? Press [Y/N]: ")
	
	if PUBLISH_SORRY_PAGE == 'Y' or PUBLISH_SORRY_PAGE == 'y':

		print("")
		print("Configuring the REDIRECT-URL now!!")
		
		url = "http://ENTER_NETSCALER_IP_HERE/nitro/v1/config/lbvserver"

		payload = json.dumps({
		"lbvserver": {
		"name": "Python-API-Test-LbVServer",
		"redirurl": "http://sorrysrvr.ENTER_COMPANY_NAME_HERE.com/"
		}
		})


		headers = {
				'Content-Type': 'application/json'
		}

		response = requests.request("PUT", url, auth=(username, password), headers=headers, data=payload)

		
		if response.status_code in [200,201,202]:
			
			print("The REDIRECT-URL was configured Successfully.")
			ADD_REDIRECT_URL=1

	##################################################################################################
	##################################### DISABLING THE VIP ##########################################
	##################################################################################################
			
			print("")
			print("DISABLING THE VIP now!!")
			
			url10 = "http://ENTER_NETSCALER_IP_HERE/nitro/v1/config/lbvserver?action=disable"

			payload10 = json.dumps({
			"lbvserver": {
			"name": "Python-API-Test-LbVServer"
			}
			})


			headers10 = {
					'Content-Type': 'application/json'
			}

			response10 = requests.request("POST", url10, auth=(username, password), headers=headers10, data=payload10)

			
			if response10.status_code in [200,201,202]:
				
				print("The VIP was DISABLED Successfully.")
				DISABLE_VIP=1
				
			else:
				
				print("The VIP could not be DISABLED.")
			
			
			
			
			
			if DISABLE_VIP == 1 and ADD_REDIRECT_URL == 1:
				FUNC_SAVE_CONFIG("ENTER_NETSCALER_IP_HERE")
			
			else:
				print("")
				print("The REDIRECT_URL could not be configured.\nPlease reach out to the Network Team or manually configure the Redirection on the Netscaler.")
			
		else:
			print("The REDIRECT-URL could not be configured.")

	elif PUBLISH_SORRY_PAGE == 'N' or PUBLISH_SORRY_PAGE == 'n':
		
		print("The user requested not to Publish the SORRY page.")
	
	else:
		
		print("")
		print("The user provided an invalid input. The SORRY page will not be published.")
	
	
	return
	


def FUNC_REDIRECT_URL_REMOVE_Python_API_Test_LbVServer():


	import requests
	import json

	username = 'ENTER_USERNAME_HERE'
	password = 'ENTER_PASSWORD_HERE'
	
	ENABLE_VIP = 0
	REMOVE_REDIRECT_URL = 0
	
##################################################################################################
#################################### REMOVE REDIRECT-URL #########################################
##################################################################################################

	print("")
	print("You have requested to Remove the Sorry Page on the test VIP Python-API-Test-LbVServer.")
	REMOVE_SORRY_PAGE = input("Are you Sure? Press [Y/N]: ")
	
	if REMOVE_SORRY_PAGE == 'Y' or REMOVE_SORRY_PAGE == 'y':

		print("")
		print("Removing the REDIRECT-URL now!!")
		
		url = "http://ENTER_NETSCALER_IP_HERE/nitro/v1/config/lbvserver?action=unset"

		payload = json.dumps({
		  "lbvserver": {
			"name": "Python-API-Test-LbVServer",
			"redirurl": "true"
		  }
		})


		headers = {
				'Content-Type': 'application/json'
		}

		response = requests.request("POST", url, auth=(username, password), headers=headers, data=payload)

		
		if response.status_code in [200,201,202]:
			
			print("The REDIRECT-URL was removed Successfully.")
			REMOVE_REDIRECT_URL=1

	##################################################################################################
	##################################### ENABLING THE VIP ##########################################
	##################################################################################################
			
			print("")
			print("ENABLING THE VIP now!!")
			
			url10 = "http://ENTER_NETSCALER_IP_HERE/nitro/v1/config/lbvserver?action=enable"

			payload10 = json.dumps({
			"lbvserver": {
			"name": "Python-API-Test-LbVServer"
			}
			})


			headers10 = {
				'Content-Type': 'application/json'
			}

			response10 = requests.request("POST", url10, auth=(username, password), headers=headers10, data=payload10)

			
			if response10.status_code in [200,201,202]:
				
				print("The VIP was ENABLED Successfully.")
				ENABLE_VIP=1
				
			else:
				
				print("The VIP could not be ENABLED.")
			
			
			
			
			
			if ENABLE_VIP == 1 and REMOVE_REDIRECT_URL == 1:
				FUNC_SAVE_CONFIG("ENTER_NETSCALER_IP_HERE")
			
			else:
				print("")
				print("The REDIRECT_URL could not be removed.\nPlease reach out to the Network Team or manually remove the Redirection on the Netscaler.")
			
		
		
		else:
			print("The REDIRECT-URL could not be removed.")


	elif REMOVE_SORRY_PAGE == 'N' or REMOVE_SORRY_PAGE == 'n':
		
		print("The user requested not to Remove the SORRY page.")
	
	else:
		
		print("")
		print("The user provided an invalid input. The SORRY page will not be removed.")
	
	
	
	
	return



def FUNC_CSR_CREATE():


	import requests
	import json

	username = 'ENTER_USERNAME_HERE'
	password = 'ENTER_PASSWORD_HERE'
	
	KEY_CREATE = 0
	CSR_CREATE = 0
	CSR_SAN_CREATE = 0	
	
##################################################################################################
######################################### CREATE KEY #############################################
##################################################################################################

	print("")	
	LB_IP = input("Enter the ip address of the Netscaler: ")
	CSR_SAN_YES_NO = input("Is the CSR for a SAN certificate? Press Y/N: ")
	
	if CSR_SAN_YES_NO == 'Y' or CSR_SAN_YES_NO == 'y':
	
		url20 = "http://" + LB_IP + "/nitro/v1/config/nsversion"

		payload20 = ""

		response20 = requests.request("GET", url20, auth=(username, password), data=payload20)
		json_data20 = response20.json()
		
		
		if response20.status_code in [200,201,202]:
			
			if 'nsversion' in json_data20:
				
				if 'NetScaler NS12.' in json_data20['nsversion']['version'] or 'NetScaler NS13.' in json_data20['nsversion']['version']:
				
					KEY_FILE_NAME = input("Enter the name of the Key to be created: ")
					KEY_FILE_SIZE_BITS = input("Enter the key size in bits: ")
					
					url = "http://" + LB_IP + "/nitro/v1/config/sslrsakey?action=create"
					
					sslrsakey = {}
					sslrsakey["keyfile"] = str(KEY_FILE_NAME)
					sslrsakey["bits"] = str(KEY_FILE_SIZE_BITS)
					
					
					payload = json.dumps({
					  "sslrsakey": {
						"keyfile": sslrsakey["keyfile"],
						"bits": sslrsakey["bits"]
					  }
					})

					
					print("")
					print("Creating the KEY now!!")
					
					headers = {
							'Content-Type': 'application/json'
					}

					response = requests.request("POST", url, auth=(username, password), headers=headers, data=payload)

					
					if response.status_code in [200,201,202]:
						
						print("The KEY was created Successfully.")
						KEY_CREATE = 1

##################################################################################################
##################################### CREATE SAN CSR #############################################
##################################################################################################

						print("")		
						CSR_FILE_NAME = input("Enter the CSR File name: ")
						CSR_COMMON_NAME = input("Enter the CSR Common name: ")
												
						url10 = "http://" + LB_IP + "/nitro/v1/config/sslcertreq?action=create"
							
						print("")
						PROVIDED_SAN_NAMES = input("Provide the CSR SAN names seperated by (,) \nExample: pitstop1.ENTER_COMPANY_NAME_HERE.com,pitstop2.ENTER_COMPANY_NAME_HERE.com\n\tDo not use wildcard characters, such as asterisk (*) or question mark (?),\n\tand do not use an IP address as the SAN name.\n\tThe SAN name must not contain the protocol specifier <http://> or <https://>.\n\nProvide the names here: ")
						CSR_SAN_NAMES = "DNS:" + str(PROVIDED_SAN_NAMES)
						
						
						sslcertreq = {}
						sslcertreq["reqfile"] = str(CSR_FILE_NAME)
						sslcertreq["keyfile"] = str(KEY_FILE_NAME)
						sslcertreq["countryname"] = "US"
						sslcertreq["statename"] = "New York"
						sslcertreq["organizationname"] = "ENTER_COMPANY_NAME_HERE Inc"
						sslcertreq["organizationunitname"] = "MTS Network"
						sslcertreq["localityname"] = "New York City"
						sslcertreq["commonname"] = str(CSR_COMMON_NAME)
						sslcertreq["subjectaltname"] = str(CSR_SAN_NAMES)
						sslcertreq["digestmethod"] = "SHA256"


						payload10 = json.dumps({
						  "sslcertreq": {
							"reqfile": sslcertreq["reqfile"],
							"keyfile": sslcertreq["keyfile"],
							"countryname": sslcertreq["countryname"],
							"statename": sslcertreq["statename"],
							"organizationname": sslcertreq["organizationname"],
							"organizationunitname": sslcertreq["organizationunitname"],
							"localityname": sslcertreq["localityname"],
							"commonname": sslcertreq["commonname"],
							"subjectaltname": sslcertreq["subjectaltname"],
							"digestmethod": sslcertreq["digestmethod"]			
						  }
						})


						
						print("")
						print("Creating the SAN CSR now!!")		
						
						headers10 = {
							'Content-Type': 'application/json'
						}

						response10 = requests.request("POST", url10, auth=(username, password), headers=headers10, data=payload10)

								
						if response10.status_code in [200,201,202]:
							
							print("The SAN CSR was created Successfully.")
							CSR_SAN_CREATE = 1
							
						else:
							
							print("The SAN CSR could not be created.")
						
						
						if KEY_CREATE == 1 and CSR_SAN_CREATE == 1:
							
							FUNC_SAVE_CONFIG(LB_IP)
							FUNC_CSR_DETAILS_FIND(LB_IP, CSR_FILE_NAME)
						
						elif KEY_CREATE == 1 and CSR_SAN_CREATE == 0:
							print("")
							print("The KEY file was created but the SAN CSR file could not be created.\nPlease reach out to the Network Team or manually create the SAN CSR on the Netscaler.")

						elif KEY_CREATE == 0 and CSR_SAN_CREATE == 0:
							print("")
							print("The KEY and SAN CSR file could not be created.\nPlease reach out to the Network Team or manually create KEY & SAN CSR on the Netscaler.")
						
						
					else:
						print("The KEY could not be created.")
			
				elif 'NetScaler NS11.' in json_data20['nsversion']['version'] or 'NetScaler NS10.' in json_data20['nsversion']['version']:
					print("")
					print("The Netscaler does not support creation of SAN CSR.\nPlease reach out to the Network Team or use openssl for SAN CSR creation.")
				
				
			else:
				print("")
				print("The Netscaler did not provide the nsversion dict in the API call.\nPlease reach out to the Network Team or use openssl for SAN CSR creation.")
		
		else:
			print("")
			print("The API call could not find the Netscaler Release.\nPlease reach out to the Network Team or use openssl for SAN CSR creation.")




	elif CSR_SAN_YES_NO == 'N' or CSR_SAN_YES_NO == 'n':

		KEY_FILE_NAME = input("Enter the name of the Key to be created: ")
		KEY_FILE_SIZE_BITS = input("Enter the key size in bits: ")
		
		url = "http://" + LB_IP + "/nitro/v1/config/sslrsakey?action=create"
		
		sslrsakey = {}
		sslrsakey["keyfile"] = str(KEY_FILE_NAME)
		sslrsakey["bits"] = str(KEY_FILE_SIZE_BITS)
		
		
		payload = json.dumps({
		  "sslrsakey": {
			"keyfile": sslrsakey["keyfile"],
			"bits": sslrsakey["bits"]
		  }
		})

		
		print("")
		print("Creating the KEY now!!")
		
		headers = {
				'Content-Type': 'application/json'
		}

		response = requests.request("POST", url, auth=(username, password), headers=headers, data=payload)

		
		if response.status_code in [200,201,202]:
			
			print("The KEY was created Successfully.")
			KEY_CREATE = 1


##################################################################################################
######################################### CREATE CSR #############################################
##################################################################################################

			print("")		
			CSR_FILE_NAME = input("Enter the CSR File name: ")
			CSR_COMMON_NAME = input("Enter the CSR Common name: ")
			
			
			url10 = "http://" + LB_IP + "/nitro/v1/config/sslcertreq?action=create"

		
			sslcertreq = {}
			sslcertreq["reqfile"] = str(CSR_FILE_NAME)
			sslcertreq["keyfile"] = str(KEY_FILE_NAME)
			sslcertreq["countryname"] = "US"
			sslcertreq["statename"] = "New York"
			sslcertreq["organizationname"] = "ENTER_COMPANY_NAME_HERE Inc"
			sslcertreq["organizationunitname"] = "MTS Network"
			sslcertreq["localityname"] = "New York City"
			sslcertreq["commonname"] = str(CSR_COMMON_NAME)
			sslcertreq["digestmethod"] = "SHA256"


			payload10 = json.dumps({
			  "sslcertreq": {
				"reqfile": sslcertreq["reqfile"],
				"keyfile": sslcertreq["keyfile"],
				"countryname": sslcertreq["countryname"],
				"statename": sslcertreq["statename"],
				"organizationname": sslcertreq["organizationname"],
				"organizationunitname": sslcertreq["organizationunitname"],
				"localityname": sslcertreq["localityname"],
				"commonname": sslcertreq["commonname"],
				"digestmethod": sslcertreq["digestmethod"]			
			  }
			})		

			
			print("")
			print("Creating the CSR now!!")		
			
			headers10 = {
				'Content-Type': 'application/json'
			}

			response10 = requests.request("POST", url10, auth=(username, password), headers=headers10, data=payload10)

					
			if response10.status_code in [200,201,202]:
				
				print("The CSR was created Successfully.")
				CSR_CREATE = 1
				
			else:
				
				print("The CSR could not be created.")
			
			
			if KEY_CREATE == 1 and CSR_CREATE == 1:
				
				FUNC_SAVE_CONFIG(LB_IP)
				FUNC_CSR_DETAILS_FIND(LB_IP, CSR_FILE_NAME)
			
			elif KEY_CREATE == 1 and CSR_CREATE == 0:
				print("")
				print("The KEY file was created but the CSR file could not be created.\nPlease reach out to the Network Team or manually create the CSR on the Netscaler.")

			elif KEY_CREATE == 0 and CSR_CREATE == 0:
				print("")
				print("The KEY and CSR file could not be created.\nPlease reach out to the Network Team or manually create KEY & CSR on the Netscaler.")
			
			
		else:
			print("The KEY could not be created.")
		
	return
	


def FUNC_SAVE_CONFIG(lb_ip):

	import requests
	import json

	username = 'ENTER_USERNAME_HERE'
	password = 'ENTER_PASSWORD_HERE'
	
##################################################################################################
################################### Saving Configuration #########################################
##################################################################################################

	lb_ip = FUNC_CHECK_NETSCALER_PRI_OR_SEC_IN_HA(lb_ip)
	
	print("")
	print("Saving the Netscaler configuration now!!")

	
	url10 = "http://" + str(lb_ip) + "/nitro/v1/config/nsconfig?action=save"

	payload10 = json.dumps({
	  "nsconfig": {}
	})


	headers10 = {
			'Content-Type': 'application/json'
	}

	response10 = requests.request("POST", url10, auth=(username, password), headers=headers10, data=payload10)

	if response10.status_code in [200,201,202]:
		print("Changes performed. Configuration Saved!!")
	else:
		print("The changes could not be saved.")
	
		
		
	return
	


def FUNC_CSR_DETAILS_FIND(LB_IP, CSR_FILE_NAME):

	import getpass
	import sys
	import telnetlib
	import time
	import socket
	import paramiko


	user = "ENTER_USERNAME_HERE"
	password = "ENTER_PASSWORD_HERE"
	
	
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	
	
	try:
		print("")
		print ("Initiating ssh connection to the Netscaler with IP: " + LB_IP)
		ssh.connect(LB_IP, port=22, username=user, password=password, timeout=2)
	except (socket.error) as message:
		print("")
		print("ERROR: SSH connection to " + LB_IP +" failed because of socket error: " +str(message))
		print("Please manually verify the CSR file details on the website https://certlogik.com/decoder/")
		sys.exit(1)
	except (paramiko.AuthenticationException) as message:
		print("")
		print("ERROR: SSH connection to " + LB_IP +" failed because of wrong credentials: " +str(message))
		print("Please manually verify the CSR file details on the website https://certlogik.com/decoder/")
		sys.exit(1)
	except (paramiko.SSHException) as message:
		print("")
		print("ERROR: SSH connection to " + LB_IP +" failed because of ssh related error: " +str(message))
		print("Please manually verify the CSR file details on the website https://certlogik.com/decoder/")
		sys.exit(1)
	except (paramiko.BadHostKeyException) as message:
		print("")
		print("ERROR: SSH connection to " + LB_IP +" failed becaus of bad host SSH key: " +str(message))
		print("Please manually verify the CSR file details on the website https://certlogik.com/decoder/")
		sys.exit(1)
		
	
	# Invoke the SSH Shell so the channel remains the same
	# The same cahnnel can be used to run multiple commands
	# Also can be used to have user interact with the Netscaler	
	client=ssh.invoke_shell()
	time.sleep(2)
	output = client.recv(65535)
	print (output.decode('ascii'))
	

	# Send 2 enter commands to create spacing in the output
	client.send("\n")
	client.send("\n")
	
	
	# Send the expert command to the Netscaler to enter the Expert Shell
	client.send("shell\n")
	time.sleep(2)
	output = client.recv(65535)
	print("")
	print(output.decode('ascii'))


	# Send 2 enter commands to create spacing in the output
	client.send("\n")
	client.send("\n")
	
	
	# Send the expert command to the Netscaler to enter the Expert Shell
	client.send("cd /nsconfig/ssl\n")
	time.sleep(2)
	output = client.recv(65535)
	print("")
	print(output.decode('ascii'))


	# Send 2 enter commands to create spacing in the output
	client.send("\n")
	client.send("\n")
	
	
	# Send the expert command to the Netscaler to enter the Expert Shell
	client.send("pwd\n")
	time.sleep(2)
	output = client.recv(65535)
	print("")
	print(output.decode('ascii'))


	# Send 2 enter commands to create spacing in the output
	client.send("\n")
	client.send("\n")

	
	print("")
	print("Transferring the CSR to the UK FTP server")
	print("")
	
	# Send the CURL command to FTP the CSR to the UK FTP server
	client.send("curl -T /nsconfig/ssl/" + CSR_FILE_NAME + " -# ftp://ENTER_FTP_SERVER_FQDN_OR__IP_HERE --user ENTER_FTP_USERNAME_HERE:ENTER_FTP_PASSWORD_HERE\n")
	time.sleep(5)
	output = client.recv(65535)
	
	if "Failed to connect to" in output.decode('ascii') or "Operation timed out" in output.decode('ascii'):
		print("")
		print("The CSR file could not be transferred to the UK FTP Server.\nPlease transfer the file manually.")
		print(output.decode('ascii'))
	else:
		print("")
		print("The CSR file transferred SUCCESSFULLY to the UK FTP Server.")
		print(output.decode('ascii'))
	

	# Send 2 enter commands to create spacing in the output
	client.send("\n")
	client.send("\n")
	
	
	
	# Send the cat command to the Netscaler to print the output of the CSR file
	client.send("cat " + CSR_FILE_NAME + " \n")
	time.sleep(2)
	output = client.recv(65535)
	print("")
	print("The Certificate Signing Request (CSR) file contents are: ")
	print(output.decode('ascii'))


	# Send 2 enter commands to create spacing in the output
	client.send("\n")
	client.send("\n")
	

	print("")
	print("Generating the CSR verification output")
	print("")

	
	# Send the openssl command to the Netscaler to verify the CSR details
	client.send("openssl req -in " + CSR_FILE_NAME + "  -noout -text\n")
	time.sleep(2)
	output = client.recv(65535)
	print("")
	print(output.decode('ascii'))
	

	# Send 2 enter commands to create spacing in the output
	client.send("\n")
	client.send("\n")


	# Send the exit command to close the EXPERT SHELL
	client.send("exit\n")


	# Send 2 enter commands to create spacing in the output
	client.send("\n")
	client.send("\n")


	# Send the exit command to close the SSH session
	client.send("exit\n")


	# Close the client channel
	# and the SSH connection
	client.close()
	ssh.close()
	
	
	return



def FUNC_CERTIFICATE_UPLOAD_TO_NETSCALER():

	import getpass
	import sys
	import telnetlib
	import time
	import socket
	import paramiko


	user = "ENTER_USERNAME_HERE"
	password = "ENTER_PASSWORD_HERE"
	
	print("")
	CERT_FILE_NAME = input("Enter the name of the Certificate file saved to the FTP server: ")
	LB_IP = input("Enter the ip address of the Netscaler to which you want to upload the certificate: ")
	
	LB_IP = FUNC_CHECK_NETSCALER_PRI_OR_SEC_IN_HA(LB_IP)
	
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	
	try:
		print("")
		print ("Initiating ssh connection to the Netscaler with IP: " + LB_IP)
		ssh.connect(LB_IP, port=22, username=user, password=password, timeout=2)
	except (socket.error) as message:
		print("")
		print("ERROR: SSH connection to " + LB_IP +" failed because of socket error: " + str(message))
		sys.exit(1)
	except (paramiko.AuthenticationException) as message:
		print("")
		print("ERROR: SSH connection to " + LB_IP +" failed because of wrong credentials: " +str(message))
		sys.exit(1)
	except (paramiko.SSHException) as message:
		print("")
		print("ERROR: SSH connection to " + LB_IP +" failed because of ssh related error: " +str(message))
		sys.exit(1)
	except (paramiko.BadHostKeyException) as message:
		print("")
		print("ERROR: SSH connection to " + LB_IP +" failed becaus of bad host SSH key: " +str(message))
		sys.exit(1)
		
	
	# Invoke the SSH Shell so the channel remains the same
	# The same cahnnel can be used to run multiple commands
	# Also can be used to have user interact with the Netscaler	
	client=ssh.invoke_shell()
	time.sleep(2)
	output = client.recv(65535)
	print (output.decode('ascii'))
	

	# Send 2 enter commands to create spacing in the output
	client.send("\n")
	client.send("\n")
	
	
	# Send the expert command to the Netscaler to enter the Expert Shell
	client.send("shell\n")
	time.sleep(2)
	output = client.recv(65535)
	print("")
	print(output.decode('ascii'))


	# Send 2 enter commands to create spacing in the output
	client.send("\n")
	client.send("\n")
	
	
	# Send the expert command to the Netscaler to enter the Expert Shell
	client.send("cd /nsconfig/ssl\n")
	time.sleep(2)
	output = client.recv(65535)
	print("")
	print(output.decode('ascii'))


	# Send 2 enter commands to create spacing in the output
	client.send("\n")
	client.send("\n")
	
	
	# Send the expert command to the Netscaler to enter the Expert Shell
	client.send("pwd\n")
	time.sleep(2)
	output = client.recv(65535)
	print("")
	print(output.decode('ascii'))


	# Send 2 enter commands to create spacing in the output
	#client.send("\n")
	#client.send("\n")
	
	
	# Send the CURL command to download the Certificate from the UK FTP server
	client.send("ftp -in ftp://ENTER_FTP_USERNAME_HERE:ENTER_FTP_PASSWORD_HERE@ENTER_FTP_SERVER_FQDN_OR__IP_HERE/" + CERT_FILE_NAME + " /nsconfig/ssl\n")
	time.sleep(2)
	output = client.recv(65535)
	print("")
	print(output.decode('ascii'))
	
	#print("")
	#print("The Certificate is uploaded to the Netscaler SUCCESSFULLY!!")	

	# Send 2 enter commands to create spacing in the output
	client.send("\n")
	client.send("\n")


	# Send the cat command to the Netscaler to print the output of the certificate file
	client.send("cat " + CERT_FILE_NAME + " \n")
	time.sleep(2)
	output = client.recv(65535)
	print("")
	print("The Certificate Signing Request (CSR) details: \n")
	print(output.decode('ascii'))


	# Send 2 enter commands to create spacing in the output
	client.send("\n")
	client.send("\n")


	# Send the exit command to close the EXPERT SHELL
	client.send("exit\n")


	# Send 2 enter commands to create spacing in the output
	client.send("\n")
	client.send("\n")


	# Send the exit command to close the SSH session
	client.send("exit\n")


	# Close the client channel
	# and the SSH connection
	client.close()
	ssh.close()
	
	
	return



def FUNC_SERVER_CERTKEY_PAIR_CREATION_CA_CERTKEY_PAIR_LINK():


	import requests
	import json

	print("")	
	LB_IP = input("Enter the ip address of the Netscaler: ")
	CERT_KEY_PAIR_NAME = input("Enter the CERT-KEY pair name: ")
	CERT_NAME = input("Enter the Certificate file name: ")
	CERT_KEY_NAME = input("Enter the RSA-Key file name: ")
	
	LB_IP = FUNC_CHECK_NETSCALER_PRI_OR_SEC_IN_HA(LB_IP)
	
	url = "http://" + str(LB_IP) + "/nitro/v1/config/sslcertkey"


	sslcertkey = {}
	sslcertkey["certkey"] = str(CERT_KEY_PAIR_NAME)
	sslcertkey["cert"] = str(CERT_NAME)
	sslcertkey["key"] = str(CERT_KEY_NAME)
	

	payload = json.dumps({
	  "sslcertkey": {
		"certkey": sslcertkey["certkey"],
		"cert": sslcertkey["cert"],
		"key": sslcertkey["key"]
	  }
	})

	
	headers = {
			'Content-Type': 'application/json'
	}


	print("")
	print("Creating the CERT-KEY pair now!!")
	

	response = requests.request("POST", url, auth=(username, password), headers=headers, data=payload)

	
	if response.status_code in [200,201,202]:
		
		print("The CERT-KEY pair created Successfully.")
		FUNC_SAVE_CONFIG(LB_IP)
		
		print("")
		print("The CERT-KEY pair created must now be linked to a Certificate Authority certificate-key pair")
		CA_CERT_KEY_PAIR_NAME = input("Enter the Certificate Authority CERT-KEY pair name to link with the server CERT-KEY pair: ")
		

		url10 = "http://" + str(LB_IP) + "/nitro/v1/config/sslcertkey?action=link"


		sslcertkey = {}
		sslcertkey["certkey"] = str(CERT_KEY_PAIR_NAME)
		sslcertkey["linkcertkeyname"] = str(CA_CERT_KEY_PAIR_NAME)

	
		payload10 = json.dumps({
		  "sslcertkey": {
			"certkey": sslcertkey["certkey"],
			"linkcertkeyname": sslcertkey["linkcertkeyname"]
		  }
		})
	
			
		headers10 = {
				'Content-Type': 'application/json'
		}

		response10 = requests.request("POST", url10, auth=(username, password), headers=headers10, data=payload10)

		if response10.status_code in [200,201,202]:
			
			print("")
			print("The server CERT-KEY pair is linked to the Certificate Authority CERT-KEY pair Successfully.")
			FUNC_SAVE_CONFIG(LB_IP)
			
		elif response.status_code in [409]:
		
			print("")
			print("The server CERT-KEY pair is already linked to the Certificate Authority CERT-KEY pair.\nThe server CERT-KEY pair is not required to be linked to CA CERT-KEY pair.")
		
		elif response.status_code in [599]:
		
			print("")
			print("The server CERT-KEY pair or the Certificate Authority CERT-KEY pair does not exists on the Netscaler.\nThe server CERT-KEY pair could not be linked to CA CERT-KEY pair.")
		
		else:
			
			print("")
			print("The server CERT-KEY pair could not be linked to the Certificate Authority CERT-KEY pair.\nPlease link them manually.")
				

	elif response.status_code in [409]:
	
		print("")
		print("The CERT-KEY pair with same name or same KEY and CERT already exists on the Netscaler and hence it could not be created.")
	
	elif response.status_code in [599]:
	
		print("")
		print("The CERT-KEY pair could not be created. Please ensure the CERT and KEY files are present on the Netscaler or the names are entered correctly.")
	
	else:
		
		print("")
		print("The CERT-KEY pair could not be created. Please create it manually.")



	return



def FUNC_SERVER_CERTKEY_PAIR_BIND_SSL_VSERVER():


	import requests
	import json
	
	print("")
	VIP_NAME = input("Enter the name of the VIP: ")
	LB_IP = input("Enter the ip address of the Netscaler hosting the VIP: ")
	SERVER_CERT_KEY_PAIR_NAME = input("Enter the Server CERT-KEY pair name: ")
	
	LB_IP = FUNC_CHECK_NETSCALER_PRI_OR_SEC_IN_HA(LB_IP)
	
	url = "http://" + str(LB_IP) + "/nitro/v1/config/sslvserver/" + str(VIP_NAME)

	payload = ""

	print("")
	print("Checking if the SSL vserver exists on the Nestcaler.")
	

	response = requests.request("GET", url, auth=(username, password), data=payload)

	
	if response.status_code in [200,201,202]:
		
		print("The SSL vServer is found on the Netscaler.")

		url10 = "http://" + str(LB_IP) + "/nitro/v1/config/sslcertkey/" + str(SERVER_CERT_KEY_PAIR_NAME)

		payload10 = ""

		print("")
		print("Checking if the Server CERT-KEY pair exists on the Nestcaler.")
		

		response10 = requests.request("GET", url10, auth=(username, password), data=payload10)
		
		
		if response.status_code in [200,201,202]:
			
			print("The Server CERT-KEY pair is found on the Netscaler.")
			
			print("")
			print("Request initiated to bind the Server CERT-KEY pair: " + str(SERVER_CERT_KEY_PAIR_NAME) + "to the SSL vserver: " + str(VIP_NAME))	



			url30 = "http://" + str(LB_IP) + "/nitro/v1/config/sslvserver_sslcertkey_binding"

			sslvserver_sslcertkey_binding = {}
			sslvserver_sslcertkey_binding["vservername"] = str(VIP_NAME)
			sslvserver_sslcertkey_binding["certkeyname"] = str(SERVER_CERT_KEY_PAIR_NAME)

		
			payload30 = json.dumps({
			  "sslvserver_sslcertkey_binding": {
				"vservername": sslvserver_sslcertkey_binding["vservername"],
				"certkeyname": sslvserver_sslcertkey_binding["certkeyname"]
			  }
			})
		
				
			headers30 = {
					'Content-Type': 'application/json'
			}
			
			
		
			response30 = requests.request("PUT", url30, auth=(username, password), headers=headers30, data=payload30)
			
			
			if response30.status_code in [200,201,202]:


				print("The Server CERT-KEY pair: " + str(SERVER_CERT_KEY_PAIR_NAME) + " is binded SUCCESSFULLY to the SSL vserver: " + str(VIP_NAME))
				
			else:
				
				print("The API call did not provide the sslvserver_sslcertkey_binding list")

		
			
			url40 = "http://" + str(LB_IP) + "/nitro/v1/config/sslcertkey_sslvserver_binding/" + str(SERVER_CERT_KEY_PAIR_NAME)

			payload40 = ""
			
			response40 = requests.request("GET", url40, auth=(username, password), data=payload40)
			json_data40 = response40.json()
			
				
			print("")
			print("\nPerforming recheck to confirm if the Server CERT-KEY pair: " + str(SERVER_CERT_KEY_PAIR_NAME) + " is binded SUCCESSFULLY to the SSL vserver: " + str(VIP_NAME))
			
				
			if 'sslcertkey_sslvserver_binding' in json_data40:
			
				for x in json_data40['sslcertkey_sslvserver_binding']:
				
					if x['certkey'] == SERVER_CERT_KEY_PAIR_NAME and x['servername'] == VIP_NAME:
						
						print("The recheck confirmed the Server CERT-KEY pair: " + str(SERVER_CERT_KEY_PAIR_NAME) + " was successfully binded to the SSL vserver: " + str(VIP_NAME))
						
						FUNC_SAVE_CONFIG(LB_IP)
						
					else:
						
						print("")
						print("The recheck confirmed the Server CERT-KEY pair: " + str(SERVER_CERT_KEY_PAIR_NAME) + " could not be binded to the SSL vserver: " + str(VIP_NAME))
						print("Please bind them manually on the Netscaler.")
						
			else:
				
				print("The API call did not provide the sslcertkey_sslvserver_binding list")		
				
		elif response.status_code in [599]:
		
			print("The Server CERT-KEY pair is not found on the Netscaler.\nPlease ensure the correct Server CERT-KEY pair name is provided in the request or the Server CERT-KEY pair exists on the Netscaler.")
			
		else:
			
			print("The Server CERT-KEY pair is not found on the Netscaler.\nPlease ensure the Server CERT-KEY pair exists on the Netscaler.")
			
		
	elif response.status_code in [404]:
		
		print("The SSL vServer was not found on the Netscaler.\nPlease ensure the correct name is provided in the request or the vserver exists on the Netscaler.")

	else:
		
		print("The SSL vServer was not found on the Netscaler.\nPlease ensure the vserver exists on the Netscaler.")



	
	return



def FUNC_REAL_SERVER_BIND_OR_UNBIND_FROM_SERVICEGROUP():


	import requests
	import json


	GOOD_SERVER_IP_ADDRESS_LIST = []
	BAD_SERVER_IP_ADDRESS_LIST = []
	SERVER_IP_ADDRESS_LIST = []
	
	SERVER_UNBIND_PASS_LIST = []
	SERVER_UNBIND_FAIL_LIST = []
	
		
	print("")	
	LB_IP = input("Enter the ip address of the Netscaler: ")

	
	print("")
	SERVER_BIND_OR_UNBIND = input("Please confirm if you want to ADD or DELETE the server from ServiceGroup.\n A - ADD and D - DELETE: ")
	
	LB_IP = FUNC_CHECK_NETSCALER_PRI_OR_SEC_IN_HA(LB_IP)


	if SERVER_BIND_OR_UNBIND == 'A' or SERVER_BIND_OR_UNBIND == 'a':
		
		
		
		print("")
		SERVICEGROUP_NAME = input("Enter the SERVICEGROUP name: ")
		


		url = "http://" + LB_IP + "/nitro/v1/config/servicegroup/" + SERVICEGROUP_NAME
		
		payload = ""

		response = requests.request("GET", url, auth=(username, password), data=payload)
		json_data = response.json()

			
		
		if response.status_code in [200,201,202]:
			
			if 'servicegroup' in json_data:	
				
				
				for x in json_data['servicegroup']:
					
					if x['servicegroupname'] == SERVICEGROUP_NAME:	

						print("")
						print("The ServiceGroup: " + SERVICEGROUP_NAME + " was found on the Netscaler.")
						print("The ServiceGroup type is: " + str(x['servicetype']))
						

						
						print("")
						NUMBER_OF_SERVERS = input("Enter the number of Servers you want to BIND: ")
						while True:
							try:
								NUMBER_OF_SERVERS = int(NUMBER_OF_SERVERS)
								break
							except:
								print("")
								print("The Value provided is not a number.")
								NUMBER_OF_SERVERS = input("Please enter a Valid number for the number of Servers you want to BIND: ")
						


						print("")
						SERVER_PORT_NUMBER = input("Enter the port number for the Servers: ")
						while True:
							try:
								SERVER_PORT_NUMBER = int(SERVER_PORT_NUMBER)									
								if SERVER_PORT_NUMBER > 0 and SERVER_PORT_NUMBER < 65536:								
									break									
								else:
									print("")
									print("The Value provided is not in the range 1-65535 number.")
									SERVER_PORT_NUMBER = input("Please enter the port number for the Servers: ")								
							except:
								print("")
								print("The Value provided is not a number.")
								SERVER_PORT_NUMBER = input("Please enter a Valid number for the port number for the Servers: ")
						
						
						
						for i in range(int(NUMBER_OF_SERVERS)):
							SERVER_COUNT = i + 1
							print("")
							print("Enter the ip address of the Server-" + str(SERVER_COUNT) + ": ")
							SERVER_IP_ADDRESS = input("")
							SERVER_IP_ADDRESS_LIST.append(SERVER_IP_ADDRESS)
							
							#print(SERVER_IP_ADDRESS_LIST)
							#print(SERVER_PORT_NUMBER)

						print("")
						print("")
						
						for SERVER_IP_ADDRESS in SERVER_IP_ADDRESS_LIST:
						

							url10 = "http://" + LB_IP + "/nitro/v1/config/server"
							
							server = {}
							server["name"] = "SRVR_" + str(SERVER_IP_ADDRESS)
							server["ipaddress"] = str(SERVER_IP_ADDRESS)
							server["state"] = "ENABLED"
							
							
							payload10 = json.dumps({
							  "server": {
								"name": server["name"],
								"ipaddress": server["ipaddress"],
								"state": server["state"]
							  }
							})

							headers10 = {
									'Content-Type': 'application/json'
							}
							
							time.sleep(1)
							response10 = requests.request("POST", url10, auth=(username, password), headers=headers10, data=payload10)
						
							
							if response10.status_code in [200,201,202]:

								#print("")
								print("The Server: " + SERVER_IP_ADDRESS + " is created SUCCESSFULLY.")
								
								#input("Press ENTER-1 to Continue")
								GOOD_SERVER_IP_ADDRESS_LIST.append(SERVER_IP_ADDRESS)
																
							elif response10.status_code in [409]:
							
								#print("")
								print("The Server: " + SERVER_IP_ADDRESS + " already exists on the Netscaler. It will not be created.")
								BAD_SERVER_IP_ADDRESS_LIST.append(SERVER_IP_ADDRESS)
								
							else:
								
								#print("")
								print("The API call failed to create the server: " + SERVER_IP_ADDRESS + ". Please create it manually and bind to the ServiceGroup.")
								BAD_SERVER_IP_ADDRESS_LIST.append(SERVER_IP_ADDRESS)
						
						FUNC_SAVE_CONFIG(LB_IP)
						
						#print("")
						#print(GOOD_SERVER_IP_ADDRESS_LIST)
						#print("")
						#print(BAD_SERVER_IP_ADDRESS_LIST)
						



############################################################################################################
################## Started the Bind for the servers in the GOOD_SERVER_IP_ADDRESS_LIST #####################
############################################################################################################

						print("")
						print("")
						
						for SERVER_IP_ADDRESS in GOOD_SERVER_IP_ADDRESS_LIST:
							
							print("")
							print("Initiated the binding of the Server: " + str(SERVER_IP_ADDRESS) + " to the ServiceGroup name: " + str(SERVICEGROUP_NAME))
							
							url20 = "http://" + LB_IP + "/nitro/v1/config/servicegroup_servicegroupmember_binding/"


							servicegroup_servicegroupmember_binding = {}
							servicegroup_servicegroupmember_binding["servicegroupname"] = str(SERVICEGROUP_NAME)
							servicegroup_servicegroupmember_binding["servername"] = "SRVR_" + str(SERVER_IP_ADDRESS)
							servicegroup_servicegroupmember_binding["port"] = str(SERVER_PORT_NUMBER)
							servicegroup_servicegroupmember_binding["state"] = "ENABLED"
							
							
							payload20 = json.dumps({
							  "servicegroup_servicegroupmember_binding": {
								"servicegroupname": servicegroup_servicegroupmember_binding["servicegroupname"],
								"servername": servicegroup_servicegroupmember_binding["servername"],
								"port": servicegroup_servicegroupmember_binding["port"],
								"state": servicegroup_servicegroupmember_binding["state"]
							  }
							})

							headers20 = {
									'Content-Type': 'application/json'
							}
							
							
							time.sleep(1)
							response20 = requests.request("PUT", url20, auth=(username, password), headers=headers20, data=payload20)
							
							
							if response20.status_code in [200,201,202]:

								print("The Server name: " + str(servicegroup_servicegroupmember_binding["servername"]) + " with ip address: " + str(SERVER_IP_ADDRESS) + " with port: " + str(SERVER_PORT_NUMBER) + " is binded SUCCESSFULLY to the ServiceGroup name: " + str(SERVICEGROUP_NAME))
								
							elif response20.status_code in [409]:
								
								print("The Server name: " + str(servicegroup_servicegroupmember_binding["servername"]) + " with ip address: " + str(SERVER_IP_ADDRESS) + " with port: " + str(SERVER_PORT_NUMBER) + " binding already exists with the ServiceGroup name: " + str(SERVICEGROUP_NAME))
							
							else:
								
								print("The API call could not bind the Server: " + str(SERVER_IP_ADDRESS) + " to the ServiceGroup name: " + str(SERVICEGROUP_NAME))
								print("Please bind the server manually")

						FUNC_SAVE_CONFIG(LB_IP)


############################################################################################################
################## Started the Bind for the servers in the BAD_SERVER_IP_ADDRESS_LIST #####################
############################################################################################################

						#print("")
						#print("")
						
						
						url30 = "http://" + LB_IP + "/nitro/v1/config/server?attrs=name,ipaddress,state"

						payload30 = ""

						response30 = requests.request("GET", url30, auth=(username, password), data=payload30)
						json_data30 = response30.json()



						if response30.status_code in [200,201,202]:
							
							if 'server' in json_data30:

								for v in json_data30['server']:
									
									for SERVER_IP_ADDRESS in BAD_SERVER_IP_ADDRESS_LIST:
									
										if v['ipaddress'] == SERVER_IP_ADDRESS:
										
											print("")
											print("Initiated the binding of the Server: " + str(SERVER_IP_ADDRESS) + " to the ServiceGroup name: " + str(SERVICEGROUP_NAME))
											
											url40 = "http://" + LB_IP + "/nitro/v1/config/servicegroup_servicegroupmember_binding/"


											servicegroup_servicegroupmember_binding = {}
											servicegroup_servicegroupmember_binding["servicegroupname"] = str(SERVICEGROUP_NAME)
											servicegroup_servicegroupmember_binding["servername"] = str(v['name'])
											servicegroup_servicegroupmember_binding["port"] = str(SERVER_PORT_NUMBER)
											servicegroup_servicegroupmember_binding["state"] = "ENABLED"
											
											
											payload40 = json.dumps({
											  "servicegroup_servicegroupmember_binding": {
												"servicegroupname": servicegroup_servicegroupmember_binding["servicegroupname"],
												"servername": servicegroup_servicegroupmember_binding["servername"],
												"port": servicegroup_servicegroupmember_binding["port"],
												"state": servicegroup_servicegroupmember_binding["state"]
											  }
											})

											headers40 = {
													'Content-Type': 'application/json'
											}
											
											time.sleep(1)		
											response40 = requests.request("PUT", url40, auth=(username, password), headers=headers40, data=payload40)
											
											
											if response40.status_code in [200,201,202]:

												print("The Server name: " + str(servicegroup_servicegroupmember_binding["servername"]) + " with ip address: " + str(SERVER_IP_ADDRESS) + " with port: " + str(SERVER_PORT_NUMBER) + " is binded SUCCESSFULLY to the ServiceGroup name: " + str(SERVICEGROUP_NAME))
												
											elif response40.status_code in [409]:
												
												print("The Server name: " + str(servicegroup_servicegroupmember_binding["servername"]) + " with ip address: " + str(SERVER_IP_ADDRESS) + " with port: " + str(SERVER_PORT_NUMBER) + " binding already exists with the ServiceGroup name: " + str(SERVICEGROUP_NAME))
											
											else:
												
												print("The API call could not bind the Server: " + str(SERVER_IP_ADDRESS) + " to the ServiceGroup name: " + str(SERVICEGROUP_NAME))
												print("Please bind the server manually")
								
							
								FUNC_SAVE_CONFIG(LB_IP)
						
			else:
				print("")
				print("The API call did not provide the servicegroup list")
						
		else:
			print("")
			print("The API call was not able to fetch ServiceGroup details.\nPlease create the ServiceGroup first or check the name is correct.\nElse, Please add the servers manually to the ServiceGroup.")


	elif SERVER_BIND_OR_UNBIND == 'D' or SERVER_BIND_OR_UNBIND == 'd':
		


		print("")
		SERVICEGROUP_NAME = input("Enter the SERVICEGROUP name: ")
		


		url = "http://" + LB_IP + "/nitro/v1/config/servicegroup/" + SERVICEGROUP_NAME
		
		payload = ""

		response = requests.request("GET", url, auth=(username, password), data=payload)
		json_data = response.json()

			
		
		if response.status_code in [200,201,202]:
			
			if 'servicegroup' in json_data:	
				
				
				for x in json_data['servicegroup']:
					
					if x['servicegroupname'] == SERVICEGROUP_NAME:	

						print("")
						print("The ServiceGroup: " + SERVICEGROUP_NAME + " was found on the Netscaler.")
						print("The ServiceGroup type is: " + str(x['servicetype']))
						

						
						print("")
						NUMBER_OF_SERVERS = input("Enter the number of Servers you want to UNBIND: ")
						while True:
							try:
								NUMBER_OF_SERVERS = int(NUMBER_OF_SERVERS)
								break
							except:
								print("")
								print("The Value provided is not a number.")
								NUMBER_OF_SERVERS = input("Please enter a Valid number for the number of Servers you want to add: ")
						


						
						for i in range(int(NUMBER_OF_SERVERS)):
							SERVER_COUNT = i + 1
							print("")
							print("Enter the ip address of the Server-" + str(SERVER_COUNT) + ": ")
							SERVER_IP_ADDRESS = input("")
							SERVER_IP_ADDRESS_LIST.append(SERVER_IP_ADDRESS)
							
							#print(SERVER_IP_ADDRESS_LIST)
							#print(SERVER_PORT_NUMBER)

						print("")
						print("")


						url10 = "http://" + LB_IP + "/nitro/v1/config/servicegroup_binding?bulkbindings=yes"

						payload10 = ""

						time.sleep(1)
						response10 = requests.request("GET", url10, auth=(username, password), data=payload10)
						json_data10 = response10.json()



						if response10.status_code in [200,201,202]:
							
							if 'servicegroup_binding' in json_data10:
							
								for y in json_data10['servicegroup_binding']:
									
									if y['servicegroupname'] == SERVICEGROUP_NAME:
									
										print("")
										print("The ServiceGroup: " + str(SERVICEGROUP_NAME) + " was found on the Netscaler.")
										
																				
										if 'servicegroup_servicegroupmember_binding' in y:
										
											for z in y['servicegroup_servicegroupmember_binding']:
											
												for z1 in SERVER_IP_ADDRESS_LIST:
												
													if z['ip'] == z1:

														print("")
														print("The server: " + str(z['servername']) + " ip address: " + str(z['ip']) + " port number: " + str(z['port']) + " is found to be binded to the ServiceGroup: " + str(SERVICEGROUP_NAME))
														print("Initiated the request to unbind the Server.")

														url20 = "http://" + str(LB_IP) + "/nitro/v1/config/servicegroup_servicegroupmember_binding/" + str(SERVICEGROUP_NAME) + "?args=servername:" + str(z['servername']) + ",port:" + str(z['port'])
													
														payload20 = ""


														headers20 = {
																'Content-Type': 'application/json'
														}

														time.sleep(1)
														response20 = requests.request("DELETE", url20, auth=(username, password), headers=headers20, data=payload20)
														json_data20 = response20.json()
														
														if response20.status_code in [200,201,202]:	

															print("The server: " + str(z['servername']) + " ip address: " + str(z['ip']) + " port number: " + str(z['port']) + " is SUCCESSFULY UNBINDED from the ServiceGroup: " + str(SERVICEGROUP_NAME))
															SERVER_UNBIND_PASS_LIST.append(z1)
															
														elif response20.status_code in [404]:
														
															print("")
															print("The server could not be unbinded as it is not binded to the ServiceGroup")
															
														else:
															
															print("")
															print("The server could not be unbinded from the ServiceGroup")
															
										else:
										
											print("The ServiceGroup: " + SERVICEGROUP_NAME + " has no servers binded to it.\nThe request to unbind the servers cannot be completed.")
										
										

							
							
							else:
								print("")
								print("The API call did not provide the servicegroup_binding list")
						
						else:
							print("")
							print("The API call could not find the ServiceGroup.\nPlease create the ServiceGroup first or check the name is correct.\nElse, Please add the servers manually to the ServiceGroup.")
							
						
						
						print("")
						print("")
						print("")
						if SERVER_UNBIND_PASS_LIST:
							print("")
							print("The below servers were unbinded successufully from the ServiceGroup")
							print(SERVER_UNBIND_PASS_LIST)
						
						SERVER_UNBIND_FAIL_SET = set(SERVER_IP_ADDRESS_LIST) - set(SERVER_UNBIND_PASS_LIST)
						SERVER_UNBIND_FAIL_LIST = list(SERVER_UNBIND_FAIL_SET)
						
						if SERVER_UNBIND_FAIL_LIST:
							print("")
							print("The below servers could not be unbinded as they are not binded to the ServiceGroup.")
							print(SERVER_UNBIND_FAIL_LIST)
						
						time.sleep(1)
						FUNC_SAVE_CONFIG(LB_IP)

	
	else:
		
		print("")
		print("The user provided an invalid input. The action to ADD or DELETE the server will not be performed.")	
	
	
	return



def FUNC_REAL_SERVER_ENABLE_OR_DISABLE_FROM_SERVICEGROUP():


	import requests
	import json



	SERVER_NAME_IP_ADDRESS_PORT_DICT = {}
	SERVER_NAME_IP_ADDRESS_PORT_LIST_OF_DICTS = []
	
	SERVER_COUNT = 0
	
	print("")	
	LB_IP = input("Enter the ip address of the Netscaler: ")

	
	print("")
	SERVER_ENABLE_OR_DISABLE = input("Please confirm if you want to ENABLE or DISABLE the server from ServiceGroup.\n E - ENABLE and D - DISABLE: ")
	
	LB_IP = FUNC_CHECK_NETSCALER_PRI_OR_SEC_IN_HA(LB_IP)


	if SERVER_ENABLE_OR_DISABLE == 'E' or SERVER_ENABLE_OR_DISABLE == 'e':
		
		
		
		print("")
		SERVICEGROUP_NAME = input("Enter the SERVICEGROUP name: ")
		


		url = "http://" + LB_IP + "/nitro/v1/config/servicegroup_binding/" + SERVICEGROUP_NAME
		
		payload = ""

		time.sleep(1)
		response = requests.request("GET", url, auth=(username, password), data=payload)
		json_data = response.json()

			
		
		if response.status_code in [200,201,202]:
			
			if 'servicegroup_binding' in json_data:	
				
				
				for x in json_data['servicegroup_binding']:
					
					if x['servicegroupname'] == SERVICEGROUP_NAME:	

						print("")
						print("The ServiceGroup: " + SERVICEGROUP_NAME + " was found on the Netscaler.")
						
						if 'servicegroup_servicegroupmember_binding' in x:
						
							for y in x['servicegroup_servicegroupmember_binding']:
							
								print("")
								print("The server name binded to ServiceGroup is: " + str(y['servername']))
								print("The server ip address binded to ServiceGroup is: " + str(y['ip']))
								print("The server port binded to ServiceGroup is: " + str(y['port']))
								print("The server state binded to ServiceGroup is: " + str(y['svrstate']))
								print("The server state was last changed on : " + str(y['statechangetimesec']))
						

							print("")
							NUMBER_OF_SERVERS = input("Enter the number of Servers you want to ENABLE: ")
							while True:
								try:
									NUMBER_OF_SERVERS = int(NUMBER_OF_SERVERS)
									break
								except:
									print("")
									print("The Value provided is not a number.")
									NUMBER_OF_SERVERS = input("Please enter a Valid number for the number of Servers you want to ENABLE: ")
							



							for i in range(int(NUMBER_OF_SERVERS)):
								SERVER_COUNT = i + 1
								
								print("")
								print("Enter the name of the Server-" + str(SERVER_COUNT) + ": ")
								SERVER_NAME = input("")
								print("Enter the ip address of the Server-" + str(SERVER_COUNT) + ": ")
								SERVER_IP_ADDRESS = input("")
							
								print("Enter the port number of the Server-" + str(SERVER_COUNT) + ": ")
								SERVER_PORT_NUMBER = input("")
								while True:
									try:
										SERVER_PORT_NUMBER = int(SERVER_PORT_NUMBER)									
										if SERVER_PORT_NUMBER > 0 and SERVER_PORT_NUMBER < 65536:								
											break									
										else:
											print("")
											print("The Value provided is not in the range 1-65535 number.")
											SERVER_PORT_NUMBER = input("Please enter the port number for the Server: ")								
									except:
										print("")
										print("The Value provided is not a number.")
										SERVER_PORT_NUMBER = input("Please enter a Valid number for the port number for the Server: ")
				
								
								SERVER_NAME_IP_ADDRESS_PORT_DICT['SERVER_NAME'] = str(SERVER_NAME)
								SERVER_NAME_IP_ADDRESS_PORT_DICT['SERVER_IP_ADDRESS'] = str(SERVER_IP_ADDRESS)
								SERVER_NAME_IP_ADDRESS_PORT_DICT['SERVER_PORT_NUMBER'] = SERVER_PORT_NUMBER
								
								#print(SERVER_NAME_IP_ADDRESS_PORT_DICT)
								
								
								
								SERVER_NAME_IP_ADDRESS_PORT_LIST_OF_DICTS.append(SERVER_NAME_IP_ADDRESS_PORT_DICT.copy())
								

							print("")
							print("")
							
							#print(SERVER_NAME_IP_ADDRESS_PORT_LIST_OF_DICTS)
							
							
							
							
							if SERVER_NAME_IP_ADDRESS_PORT_LIST_OF_DICTS:
								
								
								
								for z in SERVER_NAME_IP_ADDRESS_PORT_LIST_OF_DICTS:
							
									url10 = "http://" + LB_IP + "/nitro/v1/config/servicegroup?action=enable"

									
									headers10 = {
											'Content-Type': 'application/json'
									}

									
									servicegroup = {}
									servicegroup["servicegroupname"] = str(SERVICEGROUP_NAME)
									servicegroup["servername"] = str(z['SERVER_NAME'])
									servicegroup["port"] = z['SERVER_PORT_NUMBER']
									
									
									
									payload10 = json.dumps({
									  "servicegroup": {
										"servicegroupname": servicegroup["servicegroupname"],
										"servername": servicegroup["servername"],
										"port": servicegroup["port"]
									  }
									})


									
									
									time.sleep(1)
									response10 = requests.request("POST", url10, auth=(username, password), headers=headers10, data=payload10)
								
									
									
									if response10.status_code in [200,201,202]:

										print("")
										print("The Server: " + str(z['SERVER_NAME']) + " was ENABLED SUCCESSFULLY.")
									
																		
									elif response10.status_code in [404]:
									
										print("")
										print("The Server: " + str(z['SERVER_NAME']) + " was not ENABLED.\nPlease check the server name provided is correct and it is binded to the ServiceGroup")
										
									else:
										
										print("")
										print("The API call failed to enable the server: " + str(z['SERVER_NAME']) + ". Please enable it manually.")

								
								time.sleep(1)
								FUNC_SAVE_CONFIG(LB_IP)
							
								
							
							
							else:
								
								print("The user did not provide any server details to be ENABLED from the ServiceGroup")


						else:
						
							print("There are no servers binded to the ServieGroup. Please bind the servers first to ENABLE the Servers.")
							
						
					else:	

						print("")
						print("The ServiceGroup: " + SERVICEGROUP_NAME + " was not found on the Netscaler.")
						
						
			else:
				print("")
				print("The API call did not provide the servicegroup_binding list")
						
		else:
			print("")
			print("The API call was not able to fetch ServiceGroup to serviceGroup Member binding details.\nPlease create the ServiceGroup first or check the name is correct.\nElse, Please ENABLE the servers manually to the ServiceGroup.")


	elif SERVER_ENABLE_OR_DISABLE == 'D' or SERVER_ENABLE_OR_DISABLE == 'd':
		

		print("")
		SERVICEGROUP_NAME = input("Enter the SERVICEGROUP name: ")
		


		url = "http://" + LB_IP + "/nitro/v1/config/servicegroup_binding/" + SERVICEGROUP_NAME
		
		payload = ""

		time.sleep(1)
		response = requests.request("GET", url, auth=(username, password), data=payload)
		json_data = response.json()

			
		
		if response.status_code in [200,201,202]:
			
			if 'servicegroup_binding' in json_data:	
				
				
				for x in json_data['servicegroup_binding']:
					
					if x['servicegroupname'] == SERVICEGROUP_NAME:	

						print("")
						print("The ServiceGroup: " + SERVICEGROUP_NAME + " was found on the Netscaler.")
						
						if 'servicegroup_servicegroupmember_binding' in x:
						
							for y in x['servicegroup_servicegroupmember_binding']:
							
								print("")
								print("The server name binded to ServiceGroup is: " + str(y['servername']))
								print("The server ip address binded to ServiceGroup is: " + str(y['ip']))
								print("The server port binded to ServiceGroup is: " + str(y['port']))
								print("The server state binded to ServiceGroup is: " + str(y['svrstate']))
								print("The server state was last changed on : " + str(y['statechangetimesec']))
						

							print("")
							NUMBER_OF_SERVERS = input("Enter the number of Servers you want to DISABLE: ")
							while True:
								try:
									NUMBER_OF_SERVERS = int(NUMBER_OF_SERVERS)
									break
								except:
									print("")
									print("The Value provided is not a number.")
									NUMBER_OF_SERVERS = input("Please enter a Valid number for the number of Servers you want to DISABLE: ")
							



							for i in range(int(NUMBER_OF_SERVERS)):
								SERVER_COUNT = i + 1
								
								print("")
								print("Enter the name of the Server-" + str(SERVER_COUNT) + ": ")
								SERVER_NAME = input("")
								print("Enter the ip address of the Server-" + str(SERVER_COUNT) + ": ")
								SERVER_IP_ADDRESS = input("")
							
								print("Enter the port number of the Server-" + str(SERVER_COUNT) + ": ")
								SERVER_PORT_NUMBER = input("")
								while True:
									try:
										SERVER_PORT_NUMBER = int(SERVER_PORT_NUMBER)									
										if SERVER_PORT_NUMBER > 0 and SERVER_PORT_NUMBER < 65536:								
											break									
										else:
											print("")
											print("The Value provided is not in the range 1-65535 number.")
											SERVER_PORT_NUMBER = input("Please enter the port number for the Server: ")								
									except:
										print("")
										print("The Value provided is not a number.")
										SERVER_PORT_NUMBER = input("Please enter a Valid number for the port number for the Server: ")
				
								
								SERVER_NAME_IP_ADDRESS_PORT_DICT['SERVER_NAME'] = str(SERVER_NAME)
								SERVER_NAME_IP_ADDRESS_PORT_DICT['SERVER_IP_ADDRESS'] = str(SERVER_IP_ADDRESS)
								SERVER_NAME_IP_ADDRESS_PORT_DICT['SERVER_PORT_NUMBER'] = SERVER_PORT_NUMBER
								
								#print(SERVER_NAME_IP_ADDRESS_PORT_DICT)
								
								
								
								SERVER_NAME_IP_ADDRESS_PORT_LIST_OF_DICTS.append(SERVER_NAME_IP_ADDRESS_PORT_DICT.copy())
								

							print("")
							print("")
							
							#print(SERVER_NAME_IP_ADDRESS_PORT_LIST_OF_DICTS)
							
							
							
							
							if SERVER_NAME_IP_ADDRESS_PORT_LIST_OF_DICTS:
								
								
								
								for z in SERVER_NAME_IP_ADDRESS_PORT_LIST_OF_DICTS:
							
									url10 = "http://" + LB_IP + "/nitro/v1/config/servicegroup?action=disable"

									
									headers10 = {
											'Content-Type': 'application/json'
									}

									
									servicegroup = {}
									servicegroup["servicegroupname"] = str(SERVICEGROUP_NAME)
									servicegroup["servername"] = str(z['SERVER_NAME'])
									servicegroup["port"] = z['SERVER_PORT_NUMBER']
									
									
									
									payload10 = json.dumps({
									  "servicegroup": {
										"servicegroupname": servicegroup["servicegroupname"],
										"servername": servicegroup["servername"],
										"port": servicegroup["port"]
									  }
									})


									
									
									time.sleep(1)
									response10 = requests.request("POST", url10, auth=(username, password), headers=headers10, data=payload10)
								
									
									
									if response10.status_code in [200,201,202]:

										print("")
										print("The Server: " + str(z['SERVER_NAME']) + " was DISABLED SUCCESSFULLY.")
									
																		
									elif response10.status_code in [404]:
									
										print("")
										print("The Server: " + str(z['SERVER_NAME']) + " was not DISABLED.\nPlease check the server name provided is correct and it is binded to the ServiceGroup")
										
									else:
										
										print("")
										print("The API call failed to enable the server: " + str(z['SERVER_NAME']) + ". Please disable it manually.")

								
								time.sleep(1)
								FUNC_SAVE_CONFIG(LB_IP)
							
								
							
							
							else:
								
								print("The user did not provide any server details to be DISABLED from the ServiceGroup")


						else:
						
							print("There are no servers binded to the ServieGroup. Please bind the servers first to DISABLE the Servers.")
							
						
					else:	

						print("")
						print("The ServiceGroup: " + SERVICEGROUP_NAME + " was not found on the Netscaler.")
						
						
			else:
				print("")
				print("The API call did not provide the servicegroup_binding list")
						
		else:
			print("")
			print("The API call was not able to fetch ServiceGroup to serviceGroup Member binding details.\nPlease create the ServiceGroup first or check the name is correct.\nElse, Please DISABLE the servers manually to the ServiceGroup.")
	
	
	else:
		
		print("")
		print("The user provided an invalid input. The action to DISABLE the server will not be performed.")	
	


	
	return








print("\n\n*************************************************************************")
print("\tThe Netscaler Script can help perform below tasks")
print("*************************************************************************\n\n")

print("")
print("Press 1 to check the VIP details")
print("")
print("Press 2 to publish the sorry page with RESPONDER-POLICY on the VIP - Python-API-Test-LbVServer")
print("Press 3 to remove the sorry page with RESPONDER-POLICY on the VIP - Python-API-Test-LbVServer")
print("")
print("Press 4 to publish the sorry page with REDIRECT-URL on the VIP - Python-API-Test-LbVServer")
print("Press 5 to remove the sorry page with REDIRECT-URL on the VIP  - Python-API-Test-LbVServer")
print("")
print("Press 6 to create Certificate Signing Request (CSR)")
print("")
print("Press 7 to UPLOAD the certificate file received from the MWO team")
print("Press 8 to create the Server CERT-KEY pair and link it to the CA CERT_KEY pair on the Netscaler")
print("")
print("Press 9 to bind the Server CERT-KEY pair to the SSL vserver(VIP) on the Netscaler")
print("")
print("Press 10 to BIND or UNBIND the Real Servers from the ServiceGroup on the Netscaler")
print("")
print("Press 11 to ENABLE or DISABLE the Real Servers from the ServiceGroup on the Netscaler")


print("")
userinput = int(input("Enter your Selection: "))

if userinput == 1:
	FUNC_VIP_START()
elif userinput == 2:
	FUNC_SORRY_PAGE_PUBLISH_Python_API_Test_LbVServer()
elif userinput == 3:
	FUNC_SORRY_PAGE_REMOVE_Python_API_Test_LbVServer()
elif userinput == 4:
	FUNC_REDIRECT_URL_CONFIGURE_Python_API_Test_LbVServer()
elif userinput == 5:
	FUNC_REDIRECT_URL_REMOVE_Python_API_Test_LbVServer()
elif userinput == 6:
	FUNC_CSR_CREATE()
elif userinput == 7:
	FUNC_CERTIFICATE_UPLOAD_TO_NETSCALER()
elif userinput == 8:
	FUNC_SERVER_CERTKEY_PAIR_CREATION_CA_CERTKEY_PAIR_LINK()
elif userinput == 9:
	FUNC_SERVER_CERTKEY_PAIR_BIND_SSL_VSERVER()
elif userinput == 10:
	FUNC_REAL_SERVER_BIND_OR_UNBIND_FROM_SERVICEGROUP()	
elif userinput == 11:
	FUNC_REAL_SERVER_ENABLE_OR_DISABLE_FROM_SERVICEGROUP()	
else:
	print("")
	print("Provide value only from the list mentioned above.")
	

	




input("\n\n\n\nPress ENTER to LEAVE")

