from datetime import datetime


def validate_capturing(category, amount, date, capture_type):
	validate = {}

	if capture_type.lower() not in ['revenue', 'expenses']:
		validate['is-error'] = True
		validate['error-message'] = 'Not found'
		validate['error-code'] = 404
		return validate

	if not category or not amount or not date:
		validate['is-error'] = True
		validate['error-message'] = 'Bad payload: Missing required value'
		validate['error-code'] = 400
		return validate

	try:
		date = datetime.strptime(date, '%Y-%m-%d')
	except:
		validate['is-error'] = True
		validate['error-message'] = 'Bad payload: Invalid date format'
		validate['error-code'] = 400
		return validate

	try:
		amount = int(amount)
	except:
		validate['is-error'] = True
		validate['error-message'] = 'Bad payload: Amount must be an integer'
		validate['error-code'] = 400
		return validate

	validate['is-error'] = False
	return validate
	