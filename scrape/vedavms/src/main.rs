use itertools::Itertools;
use regex::Regex;
use reqwest;
use serde::{Deserialize, Serialize};
use std::fs::{create_dir_all, File};
use std::io::Write;

#[derive(Debug, Serialize, Deserialize)]
struct Verse {
    index: String,
    bhaga: i32,
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
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-1.1/TS%201.1%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-1.2/TS%201.2%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-1.3/TS%201.3%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-1.4/TS%201.4%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-1.5/TS%201.5%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-1.6/TS%201.6%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-1.7/TS%201.7%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-1.8/TS%201.8%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-2.1/TS%202.1%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-2.2/TS%202.2%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-2.3/TS%202.3%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-2.4/TS%202.4%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-2.5/TS%202.5%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-2.6/TS%202.6%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-3.1/TS%203.1%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-3.2/TS%203.2%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-3.3/TS%203.3%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-3.4/TS%203.4%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-3.5/TS%203.5%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-4.1/TS%204.1%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-4.2/TS%204.2%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-4.3/TS%204.3%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-4.4/TS%204.4%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-4.5/TS%204.5%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-4.6/TS%204.6%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-4.7/TS%204.7%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-5.1/TS%205.1%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-5.2/TS%205.2%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-5.3/TS%205.3%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-5.4/TS%205.4%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-5.5/TS%205.5%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-5.6/TS%205.6%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-5.7/TS%205.7%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-6.1/TS%206.1%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-6.2/TS%206.2%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-6.3/TS%206.3%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-6.4/TS%206.4%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-6.5/TS%206.5%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-6.6/TS%206.6%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-7.1/TS%207.1%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-7.2/TS%207.2%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-7.3/TS%207.3%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-7.4/TS%207.4%20Baraha%20Padam.BRH"),
        (Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([^0-9]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Padam/TS-7.5/TS%207.5%20Baraha%20Padam.BRH")
    ];
    scrape(padam, "padam/TS");
    Ok(())
}
