import re
import json

# Read input from the file named ts.itx
with open("ts.itx", "r") as input_file:
    input_text = input_file.read()

# Define a regular expression pattern to match verses
verse_pattern = re.compile(r'(\d+)\s+(\d+)\|.+?(\d+)\|.+?\|\|(.+?)\|\|', re.DOTALL)

# Find all matches in the input text
matches = verse_pattern.findall(input_text)
print(f"MATCHED COUNT {len(matches)}")

# Create a dictionary to store verses
verses_dict = {}

# Populate the dictionary with verses
for match in matches:
    verse_index = match[0]
    chapter_number = match[1]
    verse_number = match[2]
    verse_content = match[3].strip()

    verse_key = f"{chapter_number}-{verse_number}"

    verses_dict[verse_key] = {
        "index": int(verse_index),
        "chapter": int(chapter_number),
        "verse": int(verse_number),
        "content": verse_content
    }

# Convert the dictionary to JSON
verses_json = json.dumps(verses_dict, indent=2)

# Write the JSON to a file named output.json
with open("output.json", "w") as output_file:
    output_file.write(verses_json)

print("JSON written to output.json")
