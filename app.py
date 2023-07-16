from flask import Flask, request, jsonify, send_file
from flask_pymongo import PyMongo
from bson import json_util
from datetime import datetime
from openpyxl import Workbook
import tempfile

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://127.0.0.1:27017/re_api'
mongo = PyMongo(app)

collection = [
	{'id': 1, 'type': 'revenue', 'category': 'Building renovation', 'amount': 300000, 'date': '2023-04-23', 'log_date': '2023-07-14 17:31:45.655461'},
	{'id': 2, 'type': 'expenses', 'category': 'Transportation', 'amount': 10000, 'date': '2023-05-06', 'log_date': '2023-07-14 17:34:34.234008'},
	{'id': 3, 'type': 'revenue', 'category': 'Offerings', 'amount': 56000, 'date': '2023-05-07', 'log_date': '2023-07-14 17:34:03.464338'},
	{'id': 4, 'type': 'expenses', 'category': 'Fueling', 'amount': 7000, 'date': '2023-05-08', 'log_date': '2023-07-14 17:34:19.435000'}
]

def validate_capturing(form, capture_type):
	category = form.get('category')
	amount = form.get('amount')
	date = form.get('date')

	if not category or not amount or not date:
		return 'Bad payload: Missing required value', 400

	try:
		datetime.strptime(date, '%Y-%m-%d')
	except:
		return 'Bad payload: Invalid date format', 400

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
	if capture_type.lower() not in ['expenses', 'revenue']:
		return 'Not Found', 404

	start_date = request.args.get('start_date')
	end_date = request.args.get('end_date')
	try:
		start_date = datetime.strptime(start_date, '%Y-%m-%d')
		end_date = datetime.strptime(end_date, '%Y-%m-%d')
	except:
		return 'Bad payload: Invalid start_date or end_date format', 400

	matched_reports = []
	for obj in collection:
		if obj['type'] == capture_type.lower():
			obj_date = datetime.strptime(obj['date'], '%Y-%m-%d')
			if start_date <= obj_date and end_date >= obj_date :
				matched_reports.append(obj)

	response = {
		'data': matched_reports,
		'message': 'Data retrieved',
		'status': True
	}
	return jsonify(response)

@app.route('/download/<string:capture_type>/report')
def download_report(capture_type):
	"""Api endpoint to download report
	"""
	if capture_type.lower() not in ['expenses', 'revenue']:
		return 'Not Found', 404

	start_date = request.args.get('start_date')
	end_date = request.args.get('end_date')
	try:
		start_date = datetime.strptime(start_date, '%Y-%m-%d')
		end_date = datetime.strptime(end_date, '%Y-%m-%d')
	except:
		return 'Bad payload: Invalid start_date or end_date format', 400

	# Create an excel file to write to
	wb = Workbook()
	sheet = wb.active
	heading = ['S/N', 'Item', 'Amount', 'Date', 'Type']
	s_n = 1
	sheet.append(heading)

	for obj in collection:
		if obj['type'] == capture_type.lower():
			obj_date = datetime.strptime(obj['date'], '%Y-%m-%d')
			if start_date <= obj_date and end_date >= obj_date :
				row = [
					s_n,
					obj['category'],
					obj['amount'],
					obj['date'],
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