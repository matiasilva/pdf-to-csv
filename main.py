from PyPDF2 import PdfReader
import re
import argparse
import csv
from datetime import datetime
from pathlib import Path

parser = argparse.ArgumentParser(description='Extract text from bank statements (digital-born) and output to a .csv')
parser.add_argument('infile', metavar='path', nargs=1, help='relative path to PDF')
parser.add_argument('-o', '--outfile', nargs='?', default='') 
args = parser.parse_args()

pattern = re.compile(r"^(\d{2} \w{3} \d{4}) ([ \S]+)\n(\w+)([-+])£([\d,]+\.\d{2})", re.M)
reader = PdfReader(args.infile[0])
rows = list()

for page in reader.pages:
	next_match_start = 0
	txt = page.extract_text()
	while True:
		current_match = pattern.search(txt, next_match_start)
		if not current_match:
			break
		else:
			next_match_start = current_match.start() + 1

		create_dict = lambda *args: {i:eval(i) for i in args}	
		date_purchased = datetime.strptime(current_match.group(1), "%d %b %Y")
		date_purchased = date_purchased.strftime("%d/%m/%Y")
		merchant = current_match.group(2)
		flow_type = current_match.group(3).lower()
		flow = current_match.group(4)
		value = current_match.group(5)	
		rows.append(create_dict("date_purchased", "value", "flow", "merchant", "flow_type"))

fieldnames = ['merchant','flow', 'flow_type', 'value', 'date_purchased']

infile_stem = Path(args.infile[0]).stem
output_filename = args.outfile if args.outfile else infile_stem
output_filename = f'{output_filename}.csv'

with open(output_filename, 'w', newline='') as csvfile:
	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
	writer.writeheader()
	for row in rows:
		writer.writerow(row)

