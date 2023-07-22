from dotenv import load_dotenv
import os


def api_key_auth(client_key):
	server_key = os.environ.get('API_KEY')

	auth = {
		'is_authorized': False,
		'status_code': 401,
		'message': 'Unauthorized access to endpoint'
	}

	if client_key:
		key = client_key.split(' ')[0]
		value = client_key.split(' ')[1]
		if key == 'ApiKey' and server_key == value:
			auth['is_authorized'] = True
			auth['status_code'] = 200
			auth['message'] = 'Ok'

	return auth
