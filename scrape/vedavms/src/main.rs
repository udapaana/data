use reqwest;
use serde::{Deserialize, Serialize};
use std::fs::File;
use std::io::Write;

#[derive(Debug, Serialize, Deserialize)]
struct Verse {
    index: String,
    text: String,
}

fn extract_verses(text: &str) -> Vec<Verse> {
    let pattern =
        regex::Regex::new(r"TS (\d+\.\d+\.\d+\.\d+)\n([\s\S]*?)(?:\nTS \d+\.\d+\.\d+\.\d+|$)")
            .unwrap();
    let mut verses = Vec::new();

    for cap in pattern.captures_iter(text) {
        let verse_index = cap[1].to_string();
        let verse_text = cap[2].trim().to_string();

        verses.push(Verse {
            index: verse_index,
            text: verse_text,
        });
    }

    verses
}

fn scrape() -> Result<(), Box<dyn std::error::Error>> {
    let url =
        "https://raw.githubusercontent.com/KYVeda/texts/master/saMhitA/01/TS%201%20Baraha.brh";

    let response = reqwest::blocking::get(url)?;
    let text = response.text()?;

    let verses = extract_verses(&text);

    for verse in verses {
        let json_string = serde_json::to_string_pretty(&verse)?;
        let file_name = format!("../outputs/TS-{}.json", verse.index);
        let mut file = File::create(file_name)?;
        file.write_all(json_string.as_bytes())?;
    }
    Ok(())
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    scrape();

    Ok(())
}
