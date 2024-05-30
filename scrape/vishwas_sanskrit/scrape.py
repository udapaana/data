import requests
import json
import re


def strip_index(input_string: str) -> str:
    pattern = r'\s*\[\d+\]\s*'
    cleaned_string = re.sub(pattern, '', input_string)

    return cleaned_string


def main():
    # URLs to fetch the Sanskrit text from
    urls = [
        "https://raw.githubusercontent.com/udapaana/raw_etexts/master/vedaH/yajur/taittirIya/mUlam/saMhitA/1/1.md",
        # Add more URLs here if needed
    ]

    # Iterate over URLs
    for file_index, url in enumerate(urls):

        kanda = url.split('/')[-2]
        prapathaka = url.split("/")[-1].strip(".md")

        # Fetch text from URL
        response = requests.get(url)
        text = response.text

        # Parse verses
        verses = parse_verses(text)

        parsed = []
        # Output each verse as JSON
        for index, verse in enumerate(verses):
            json_output = {
                "kanda": kanda,
                "prapathaka": prapathaka,
                "anuvaka": index+1,
                "deva": strip_index(verse),
            }
            parsed.append(
                json_output
            )

        # Write JSON to file
        with open(f"outputs/{file_index}.json", "w", encoding='utf8') as file:
            json.dump(parsed, file, indent=4)


def parse_verses(text):
    # Assuming each verse is separated by a newline
    return [line.strip() for line in text.split('\n') if line.strip()]


if __name__ == "__main__":
    main()
