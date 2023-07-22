from flask import Flask, request, jsonify, send_file
from pymongo.mongo_client import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import os

from validate_capturing import validate_capturing
from save_to_excel import save_to_excel
from validate_report import validate_report
from fetch_report import fetch_report


app = Flask(__name__)

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


@app.route('/capture/expenses', methods=['POST'])
def capture_expenses():
	"""Api endpoint to capture expenses
	"""
	category = request.form.get('category')
	amount = request.form.get('amount')
	date = request.form.get('date')

	validate = validate_capturing(category, amount, date)
	if validate['error']:
		return validate['error-message'], validate['error-code']

	payload = {
		'category': category,
		'amount': amount,
		'date': date,
		'type': 'expenses',
		'log_date': datetime.now()
	}
	data.insert_one(payload)

	response = {
		'data': None,
		'message': f"Expense recorded",
		'status': True
	}
	return jsonify(response), 201


@app.route('/capture/revenue', methods=['POST'])
def capture_revenue():
	"""Api endpoint to capture revenue
	"""
	category = request.form.get('category')
	amount = request.form.get('amount')
	date = request.form.get('date')

	validate = validate_capturing(category, amount, date)
	if validate['error']:
		return validate['error-message'], validate['error-code']

	payload = {
		'category': category,
		'amount': amount,
		'date': date,
		'type': 'revenue',
		'log_date': datetime.now()
	}
	data.insert_one(payload)

	response = {
		'data': None,
		'message': f"Revenue recorded",
		'status': True
	}
	return jsonify(response), 201


@app.route('/view/<string:capture_type>/report')
def view_report(capture_type):
	"""Api endpoint to view report
	"""
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
	validate = validate_report(request.args, capture_type)
	if validate['is-error']:
		return validate['error-message'], validate['status-code']

	start_date = validate['start-date']
	end_date = validate['end-date']
	matched_reports = fetch_report(data, start_date, end_date, capture_type)
	filename = save_to_excel(matched_reports)
	
	# Return file to user for downloading
	return send_file(filename, as_attachment=True, download_name=f"{capture_type}_data.xlsx")


@app.route('/')
def home():
	return jsonify(list(data.find({}, {'_id': 0})))


if __name__ == '__main__':
	app.run(debug=True)