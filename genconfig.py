import csv
import json

res = {}
with open("userlist.csv", newline="", encoding='utf-8') as CSVFile:
    reader = csv.DictReader(CSVFile)
    for row in reader:
        res[row["name"]] = f"{row['room']}-{row['seat']}"
with open("userlist.json", mode="w") as writer:
    writer.write(str(res))