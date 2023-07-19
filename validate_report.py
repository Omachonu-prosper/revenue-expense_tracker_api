from datetime import datetime


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