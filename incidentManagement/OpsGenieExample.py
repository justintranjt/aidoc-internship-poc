# import statements
from opsgenie.swagger_client import AlertApi
from opsgenie.swagger_client import configuration
from opsgenie.swagger_client.models import *
from opsgenie.swagger_client.rest import ApiException

configuration.api_key['Authorization'] = 'f50c1096-fe77-4e25-8dfb-d88d5d920c32'
# You can use base64 version of apiKey instead of prefix
configuration.api_key_prefix['Authorization'] = 'GenieKey'

client = AlertApi()

# create alert
body = CreateAlertRequest(
	message='AppServer1 is down!',
	alias='Tron',
	description='CPU usage is over 87%',
	teams=[TeamRecipient(name='ops_team')],
	visible_to=[TeamRecipient(name='ops_team', type='team')],
	actions=['ping', 'restart'],
	tags=['network', 'operations', 'gomtan'],
	entity='ApppServer1',
	priority='P1',
	user='user@opsgenie.com',
	note='Alert created')

try:
	response = AlertApi().create_alert(body=body)

	print('request id: {}'.format(response.request_id))
	print('took: {}'.format(response.took))
	print('result: {}'.format(response.result))
except ApiException as err:
	print("Exception when calling AlertApi->create_alert: %s\n" % err)

# Acknowledge an alert
body = AcknowledgeAlertRequest(
	user='user@opsgenie.com')

try:
	response = AlertApi().acknowledge_alert(
		identifier='Tron',
		identifier_type='alias',
		body=body)
	
	print('request id: {}'.format(response.request_id))
	print('took: {}'.format(response.took))
	print('result: {}'.format(response.result))
except ApiException as err:
	print("Exception when calling AlertApi->acknowledge_alert: %s\n" % err)

# Close an alert
body = CloseAlertRequest(
	user='user@opsgenie.com')

try:
	response = AlertApi().close_alert(
		identifier='Tron',
		identifier_type='alias',
		body=body)
	
	print('request id: {}'.format(response.request_id))
	print('took: {}'.format(response.took))
	print('result: {}'.format(response.result))
except ApiException as err:
	print("Exception when calling AlertApi->acknowledge_alert: %s\n" % err)