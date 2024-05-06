use itertools::Itertools;
use regex::Regex;
use reqwest;
use serde::{Deserialize, Serialize};
use std::fs::File;
use std::io::Write;
use std::collections::HashMap;

#[derive(Debug, Serialize, Deserialize)]
struct Verse {
    index: String,
    bhaga: i32,
    kanda: i32,
    prasna: i32,
    panasa: i32,
    text: String,
}

fn extract_verses(text: &str, pattern: &Regex, verses: &mut HashMap<String, Verse>) {
    for cap in pattern.captures_iter(text) {
        let verse_index = cap.get(1).unwrap().as_str().to_string();
        let index_parts: Vec<i32> = verse_index
            .split('.')
            .map(|x| x.parse::<i32>().unwrap())
            .collect();

        let verse_text = cap.get(2).unwrap().as_str().trim().to_string();

        if index_parts.len() == 4 {
            let bhaga = index_parts[0];
            let kanda = index_parts[1];
            let prasna = index_parts[2];
            let panasa = index_parts[3];

            let verse = Verse {
                index: verse_index.clone(),
                bhaga,
                kanda,
                prasna,
                panasa,
                text: verse_text.clone(),
            };

            verses.insert(verse_index.clone(), verse);
        }
    }
}
fn scrape(
    patterns_and_urls: Vec<(Regex, &str)>,
    naming: &str,
) -> Result<(), Box<dyn std::error::Error>> {
    
    let mut verses: HashMap<String, Verse> = HashMap::new();
    for pattern_and_url in patterns_and_urls.iter() {
        let response = reqwest::blocking::get(pattern_and_url.1)?;
        let text = response.text()?;
        extract_verses(&text, &pattern_and_url.0, &mut verses);
    }
    println!("Fetched all the urls.");
    let json_string = serde_json::to_string_pretty(&verses)?;

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

    let kramam = vec![
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-1.1/TS%201.1%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-1.2/TS%201.2%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-1.3/TS%201.3%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-1.4/TS%201.4%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-1.5/TS%201.5%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-1.6/TS%201.6%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-1.7/TS%201.7%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-1.8/TS%201.8%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-2.1/TS%202.1%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-2.2/TS%202.2%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-2.3/TS%202.3%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-2.4/TS%202.4%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-2.5/TS%202.5%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-2.6/TS%202.6%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-3.1/TS%203.1%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-3.2/TS%203.2%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-3.3/TS%203.3%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-3.4/TS%203.4%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-3.5/TS%203.5%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-4.1/TS%204.1%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-4.2/TS%204.2%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-4.3/TS%204.3%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-4.4/TS%204.4%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-4.5/TS%204.5%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-4.6/TS%204.6%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-4.7/TS%204.7%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-5.1/TS%205.1%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-5.2/TS%205.2%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-5.3/TS%205.3%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-5.4/TS%205.4%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-5.5/TS%205.5%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-5.6/TS%205.6%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-5.7/TS%205.7%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-6.1/TS%206.1%20Krama%20Paaatm%20Sanskrit.BRH"),
       (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-6.2/TS%206.2%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-6.3/TS%206.3%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-6.4/TS%206.4%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-6.5/TS%206.5%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-6.6/TS%206.6%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-7.1/TS%207.1%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-7.2/TS%207.2%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-7.3/TS%207.3%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-7.4/TS%207.4%20Krama%20Paaatm%20Sanskrit.BRH"),
        (Regex::new(r"T\.S\.(\d+\.\d+\.\d+\.\d+) - kramam\n([^(\n]+)").unwrap(), "https://raw.githubusercontent.com/KYVeda/texts/master/TS-Kramam/TS-7.5/TS%207.5%20Krama%20Paaatm%20Sanskrit.BRH")
    ];

    scrape(samhita, "samhita/TS")?;
    scrape(padam, "padam/TS");
    //scrape(kramam, "kramam/TS");
    Ok(())
}
