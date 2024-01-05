use itertools::Itertools;
use regex::Regex;
use reqwest;
use serde::{Deserialize, Serialize};
use std::fs::{create_dir_all, File};
use std::io::Write;

#[derive(Debug, Serialize, Deserialize)]
struct Verse {
    index: String,
    bhaga: i32, // Corrected field name
    kanda: i32,
    prasna: i32,
    panasa: i32,
    text: String,
}

fn extract_verses(text: &str, pattern: &Regex) -> Vec<Verse> {
    let mut verses = Vec::new();

    for cap in pattern.captures_iter(text) {
        let verse_index = cap[1].to_string();
        let index_parts: (i32, i32, i32, i32) = verse_index
            .split(".")
            .map(|x| x.to_string().parse::<i32>().unwrap())
            .collect_tuple()
            .unwrap();
        let verse_text = cap[2].trim().to_string();

        verses.push(Verse {
            index: verse_index,
            bhaga: index_parts.0, // Corrected field name
            kanda: index_parts.1,
            prasna: index_parts.2,
            panasa: index_parts.3,
            text: verse_text,
        });
    }

    verses
}
fn scrape(
    patterns_and_urls: Vec<(Regex, &str)>,
    naming: &str,
) -> Result<(), Box<dyn std::error::Error>> {
    let mut all_verses = Vec::new();

    for pattern_and_url in patterns_and_urls.iter() {
        let response = reqwest::blocking::get(pattern_and_url.1)?;
        let text = response.text()?;
        let verses = extract_verses(&text, &pattern_and_url.0);
        all_verses.extend(verses);
    }
    println!("Fetched all the urls.");
    let json_string = serde_json::to_string_pretty(&all_verses)?;

    let file_name = format!("./outputs/{}.json", naming);
    let mut file = File::create(file_name)?;
    file.write_all(json_string.as_bytes())?;

    Ok(())
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let samhita: Vec<(Regex, &str)> = vec![
        (
            Regex::new(r"TS (\d+\.\d+\.\d+\.\d+)\n([\s\S]*?)(?:TS \d+\.\d+\.\d+\.\d+|$)").unwrap(),
            "https://raw.githubusercontent.com/KYVeda/texts/master/saMhitA/01/TS%201%20Baraha.brh",
        ),
        (
            Regex::new(r"TS (\d+\.\d+\.\d+\.\d+)\n([\s\S]*?)(?:TS \d+\.\d+\.\d+\.\d+|$)").unwrap(),
            "https://raw.githubusercontent.com/KYVeda/texts/master/saMhitA/03/TS%203%20Baraha.BRH",
        ),
        (
            Regex::new(r"TS (\d+\.\d+\.\d+\.\d+)\n([\s\S]*?)(?:\nTS \d+\.\d+\.\d+\.\d+|$)")
                .unwrap(),
            "https://raw.githubusercontent.com/KYVeda/texts/master/saMhitA/02/TS%202%20Baraha.brh",
        ),
        (
            Regex::new(r"TS (\d+\.\d+\.\d+\.\d+)\n([\s\S]*?)(?:\nTS \d+\.\d+\.\d+\.\d+|$)")
                .unwrap(),
            "https://raw.githubusercontent.com/KYVeda/texts/master/saMhitA/04/TS%204%20Baraha.BRH",
        ),
        (
            Regex::new(r"TS (\d+\.\d+\.\d+\.\d+)\n([\s\S]*?)(?:\nTS \d+\.\d+\.\d+\.\d+|$)")
                .unwrap(),
            "https://raw.githubusercontent.com/KYVeda/texts/master/saMhitA/05/TS%205%20Baraha.BRH",
        ),
        (
            Regex::new(r"TS (\d+\.\d+\.\d+\.\d+)\n([\s\S]*?)(?:\nTS \d+\.\d+\.\d+\.\d+|$)")
                .unwrap(),
            "https://raw.githubusercontent.com/KYVeda/texts/master/saMhitA/06/TS%206%20Baraha.BRH",
        ),
        (
            Regex::new(r"TS (\d+\.\d+\.\d+\.\d+)\n([\s\S]*?)(?:\nTS \d+\.\d+\.\d+\.\d+|$)")
                .unwrap(),
            "https://raw.githubusercontent.com/KYVeda/texts/master/saMhitA/07/TS%207%20Baraha.BRH",
        ),
    ];
    scrape(samhita, "samhita/TS")?;

    let padam = vec![
        (
                Regex::new(r"(\d+(\.\d+){3})\n([\s\S]*?)(?:\n\d+\.\d+\.\d+\.\d+|$)").unwrap(),
                "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-1.1/TS%201.1%20Baraha%20Padam.BRH"
        )
    ];
    scrape(padam, "padam/TS");
    Ok(())
}
