from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

collection = [
	{'id': 1, 'type': 'revenue', 'category': 'Building renovation', 'amount': 300000, 'date': '2023-04-23', 'log_date': '2023-07-14 17:31:45.655461'},
	{'id': 2, 'type': 'expenses', 'category': 'Transportation', 'amount': 10000, 'date': '2023-05-06', 'log_date': '2023-07-14 17:34:34.234008'},
	{'id': 3, 'type': 'revenue', 'category': 'Offerings', 'amount': 56000, 'date': '2023-05-07', 'log_date': '2023-07-14 17:34:03.464338'},
	{'id': 4, 'type': 'expeneses', 'category': 'Fueling', 'amount': 7000, 'date': '2023-05-08', 'log_date': '2023-07-14 17:34:19.435000'}
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
		'id': len(collection) + 1,
		'category': category,
		'amount': amount,
		'date': date,
		'type': capture_type,
		'log_date': datetime.now()
	}
	collection.append(payload)

	response = {
		'data': None,
		'message': f"{capture_type.title()} recorded",
		'status': True
	}
	return jsonify(response)


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


@app.route('/')
def home():
	return jsonify(collection)

if __name__ == '__main__':
	app.run(debug=True)