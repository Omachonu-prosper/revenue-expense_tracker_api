from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pymongo.mongo_client import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import os

from controllers.validate_capturing import validate_capturing
from controllers.save_to_excel import save_to_excel
from controllers.validate_report import validate_report
from controllers.fetch_report import fetch_report
from controllers.auth import api_key_auth


app = Flask(__name__)

# Handle CORS errors
CORS(app)

# Load all environment variables stored in .env files
load_dotenv()

# If we are working in a production environment (deployed state)
# the database to be used will be the mongodb atlas database
# else the local mongodb instance will be used
app_status = os.environ.get('APP_STATUS')
if app_status == 'production':
	db_username = os.environ['DATABASE_USER']
	db_passwd = os.environ['DATABASE_PASSWORD']
	db_url = os.environ['DATABASE_URL']
	uri = f"mongodb+srv://{db_username}:{db_passwd}@{db_url}"
else:
	uri = "mongodb://127.0.0.1:27017"


client = MongoClient(uri)
db = client['re_api']
data = db['data']


@app.route('/capture/<string:capture_type>', methods=['POST'])
def capture_data(capture_type):
	"""Api endpoint to capture expenses or revenue
	"""
	auth = api_key_auth(request.headers.get('Authorization'))
	if not auth['is_authorized']:
		return auth['message'], auth['status_code']

	category = request.form.get('category')
	amount = request.form.get('amount')
	date = request.form.get('date')

	validate = validate_capturing(category, amount, date, capture_type)
	if validate['is-error']:
		return validate['error-message'], validate['error-code']

	payload = {
		'category': category,
		'amount': int(amount),
		'date': datetime.strptime(date, '%Y-%m-%d'),
		'type': capture_type,
		'log_date': datetime.now()
	}
	data.insert_one(payload)

	response = {
		'data': None,
		'message': f"{capture_type.lower()} recorded",
		'status': True
	}
	return jsonify(response), 201


@app.route('/view/<string:capture_type>/report')
def view_report(capture_type):
	"""Api endpoint to view report
	"""
	auth = api_key_auth(request.headers.get('Authorization'))
	if not auth['is_authorized']:
		return auth['message'], auth['status_code']

	validate = validate_report(request.args, capture_type)
	if validate['is-error']:
		return validate['error-message'], validate['status-code']

	start_date = validate['start-date']
	end_date = validate['end-date']
	matched_reports = fetch_report(data, start_date, end_date, capture_type)

	response = {
		'data': list(matched_reports),
		'message': 'Data retrieved',
		'status': True
	}
	return jsonify(response)


@app.route('/download/<string:capture_type>/report')
def download_report(capture_type):
	"""Api endpoint to download report
	"""
	auth = api_key_auth(request.headers.get('Authorization'))
	if not auth['is_authorized']:
		return auth['message'], auth['status_code']
	
	validate = validate_report(request.args, capture_type)
	if validate['is-error']:
		return validate['error-message'], validate['status-code']

	start_date = validate['start-date']
	end_date = validate['end-date']
	matched_reports = fetch_report(data, start_date, end_date, capture_type)
	filename = save_to_excel(matched_reports)
	
	# Return file to user for downloading
	return send_file(filename, as_attachment=True, download_name=f"{capture_type}_data.xlsx")


if __name__ == '__main__':
	if os.environ.get('APP_STATUS') == 'production':
		app.run()
	else:
		app.run(debug=True)
