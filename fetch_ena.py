import requests
import json

headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
}
#'fields': 'description,scientific_name,specimen_voucher,country,accession,tax_division,tax_id,topology',

data = {
  'result': 'sequence_release',
  'query': 'specimen_voucher="RMNH*"',
  'fields': 'scientific_name,specimen_voucher,country,accession,tax_id',
  'format': 'json',
  'limit': '2'
}


def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)


response = requests.post('https://www.ebi.ac.uk/ena/portal/api/search', headers=headers, data=data)

raw = response.json()

for item in raw: 
    item['type'] = "Digital Specimen"

jprint(raw)
