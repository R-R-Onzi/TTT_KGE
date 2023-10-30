import json
import csv
import xml.etree.ElementTree as ET

with open('population_density.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file) 
    population_data = []
    for row in csv_reader:
        row['numero_circ'] = int(row['numero_circ'])
        row['population_density'] = float(row['population_density'])
        population_data.append(row)

tree = ET.parse('circoscrizioni.kml')
root = tree.getroot()

out_csv = open("city_areas.txt", "w")
out_csv.write("id\tname\tpopulation_density\tboundary\n")

for child in root[0][1][1:]:
    number = child[3][0][0].text
    name = child[3][0][3].text

    coords = ",".join([x.replace(",", " ") for x in child[4][0][0][0].text.split(" ")])
    coords = f"POLYGON(({coords}))"
    
    density = None
    for x in population_data:
        if x['numero_circ'] == int(number):
            density = x['population_density']            

    out_csv.write(f"{number}\t{name}\t{density}\t{coords}\n")
    