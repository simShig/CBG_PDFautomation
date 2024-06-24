import json

# Load the JSON data from a file
with open('citations.json', 'r') as file:
    data = json.load(file)

# Iterate through each item and add the "isDownloaded" field with value set to false
for item in data.values():
    item['isDownloaded'] = False

# Save the modified JSON data back to the file
with open('citations.json', 'w') as file:
    json.dump(data, file, indent=4)

print("The 'isDownloaded' field has been added to each item in the JSON file.")
