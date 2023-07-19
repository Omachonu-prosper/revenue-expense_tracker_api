def fetch_report(mongo, start_date, end_date, capture_type):
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
	return matched_reports