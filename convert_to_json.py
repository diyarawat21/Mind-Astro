import csv
import json

input_csv = 'static/world-cities.csv'     # path to your downloaded file
output_json = 'static/indian_cities.json' # output path

indian_cities = []

with open(input_csv, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row['country'] == 'India':
            indian_cities.append({
                'name': row['name'],
                'state': row['subcountry']
            })

with open(output_json, 'w', encoding='utf-8') as jsonfile:
    json.dump(indian_cities, jsonfile, indent=2, ensure_ascii=False)

print(f"✅ Saved {len(indian_cities)} Indian cities to indian_cities.json")
