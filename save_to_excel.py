from openpyxl import Workbook
import tempfile


def save_to_excel(matched_reports):
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
	return filename