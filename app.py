from flask import Flask, request, jsonify, send_file
from flask_pymongo import PyMongo
from bson import json_util
from datetime import datetime
from openpyxl import Workbook
import tempfile

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://127.0.0.1:27017/re_api'
mongo = PyMongo(app)

def validate_capturing(form, capture_type):
	category = form.get('category')
	amount = form.get('amount')
	date = form.get('date')

	if not category or not amount or not date:
		return 'Bad payload: Missing required value', 400

	try:
		date = datetime.strptime(date, '%Y-%m-%d')
	except:
		return 'Bad payload: Invalid date format', 400

	try:
		amount = int(amount)
	except:
		return 'Bad payload: Amount must be an integer', 400

	payload = {
		'category': category,
		'amount': amount,
		'date': date,
		'type': capture_type,
		'log_date': datetime.now()
	}
	mongo.db.data.insert_one(payload)

	response = {
		'data': None,
		'message': f"{capture_type.title()} recorded",
		'status': True
	}
	return jsonify(response), 201


def validate_report(args, capture_type):
	response = {
		'is-error': False
	}
	if capture_type.lower() not in ['expenses', 'revenue']:
		response['is-error'] = True
		response['error-message'] = 'Not Found'
		response['status-code'] = 400
		return response

	start_date = args.get('start-date')
	end_date = args.get('end-date')
	try:
		start_date = datetime.strptime(start_date, '%Y-%m-%d')
		end_date = datetime.strptime(end_date, '%Y-%m-%d')
	except:
		response['is-error'] = True
		response['error-message'] = 'Bad payload: Invalid start_date or end_date format'
		response['status-code'] = 400
		return response

	response['start-date'] = start_date
	response['end-date'] = end_date
	return response


@app.route('/capture/expenses', methods=['POST'])
def capture_expenses():
	"""Api endpoint to capture expenses
	"""
	return validate_capturing(request.form, 'expenses')


@app.route('/capture/revenue', methods=['POST'])
def capture_revenue():
	"""Api endpoint to capture revenue
	"""
	return validate_capturing(request.form, 'revenue')


@app.route('/view/<string:capture_type>/report')
def view_report(capture_type):
	"""Api endpoint to view report
	"""
	validate = validate_report(request.args, capture_type)
	if validate['is-error']:
		return validate['error-message'], validate['status-code']

	start_date = validate['start-date']
	end_date = validate['end-date']
	matched_reports = mongo.db.data.find(
		{
			'date': {
				'$gte': start_date,
				'$lte': end_date
			},
			'type': capture_type
		},
		{'_id': 0}
	)

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
	matched_reports = mongo.db.data.find(
		{
			'date': {
				'$gte': start_date,
				'$lte': end_date
			},
			'type': capture_type
		},
		{'_id': 0}
	)
	
	# Create an excel file to write to
	wb = Workbook()
	sheet = wb.active
	heading = ['S/N', 'Item', 'Amount', 'Date', 'Type']
	s_n = 1
	sheet.append(heading)

	for obj in matched_reports:
		row = [
			s_n,
			obj['category'],
			obj['amount'],
			str(obj['date']),
			obj['type']
		]
		sheet.append(row)
		s_n += 1

	# Save excel file temporarily on the server
	with tempfile.NamedTemporaryFile(delete=False) as tmp:
		filename = tmp.name
		wb.save(filename)

	# Return file to user for downloading
	return send_file(filename, as_attachment=True, download_name=f"{capture_type}_data.xlsx")


@app.route('/')
def home():
	return jsonify(list(mongo.db.data.find({}, {'_id': 0})))


if __name__ == '__main__':
	app.run(debug=True)