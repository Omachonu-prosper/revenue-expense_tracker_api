from datetime import datetime


def validate_capturing(category, amount, date):
	validate = {}

	if not category or not amount or not date:
		return 'Bad payload: Missing required value', 400

	try:
		date = datetime.strptime(date, '%Y-%m-%d')
	except:
		validate['error'] = True
		validate['error-message'] = 'Bad payload: Invalid date format'
		validate['error-code'] = 400
		return validate

	try:
		amount = int(amount)
	except:
		validate['error'] = True
		validate['error-message'] = 'Bad payload: Amount must be an integer'
		validate['error-code'] = 400
		return validate

	validate['error'] = False
	return validate
	