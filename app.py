from flask import Flask, request, jsonify, send_file
from pymongo.mongo_client import MongoClient
from datetime import datetime

from validate_capturing import validate_capturing
from save_to_excel import save_to_excel
from validate_report import validate_report
from fetch_report import fetch_report


app = Flask(__name__)
uri = "mongodb+srv://re_api_admin:re_api_password@re-api-cluster1.fvlpwol.mongodb.net/?retryWrites=true&w=majority"
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

	payload = {}
	payload['category'] = category
	payload['amount'] = amount
	payload['date'] = date
	payload['type'] = 'expenses'
	payload['log_date'] = datetime.now()
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

	payload = {}
	payload['category'] = category
	payload['amount'] = amount
	payload['date'] = date
	payload['type'] = 'revenue'
	payload['log_date'] = datetime.now()
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