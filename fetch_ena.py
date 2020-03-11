import requests
import json

headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
}
#'fields': 'description,scientific_name,specimen_voucher,country,accession,tax_division,tax_id,topology',

data = {
  'result': 'sequence_release',
  'query': 'specimen_voucher="RMNH*"',
  'fields': 'scientific_name,specimen_voucher,accession,tax_id,last_updated,sequence_md5,country',
  'format': 'json',
  'limit': '2'
}

#curl -X POST -H "Content-Type: application/x-www-form-urlencoded" -d "result=sequence_release&query=specimen_voucher%3D%22RMNH*%22&fields=specimen_voucher%2Cscientific_name%2Caccession%2Ctax_id%2Ccollected_by%2Clast_updated%2Chost%2Clab_host%2Cdescription%2Ccollection_date&format=tsv" "https://www.ebi.ac.uk/ena/portal/api/search"


def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)


response = requests.post('https://www.ebi.ac.uk/ena/portal/api/search', headers=headers, data=data)

raw = response.json()

#for item in raw: 
#    item['type'] = "Digital Specimen"

jprint(raw)
