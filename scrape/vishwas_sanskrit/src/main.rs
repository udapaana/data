use reqwest::blocking::get;
use serde_json::json;
use std::collections::HashMap;
use std::error::Error;
use std::fs::File;
use std::io::Write;

fn get_samhita_urls() -> Vec<String> {
    let samhita: String = "https://raw.githubusercontent.com/udapaana/raw_etexts/master/vedaH/yajur/taittirIya/mUlam/saMhitA".to_string();
    // Each (k,p) value represents the number of p prasnas
    // for the corresponding kanda starting with 1 and including the value listed.
    let stubs: Vec<(i32, i32)> = vec![(1, 7), (2, 6), (3, 5), (4, 7), (5, 7), (6, 6), (7, 5)];
    let mut urls: Vec<String> = vec![];
    for &(k, bound) in stubs.iter() {
        for p in 1..bound + 1 {
            urls.push(
                samhita.clone()
                    + "/"
                    + k.to_string().as_str()
                    + "/"
                    + p.to_string().as_str()
                    + ".md",
            );
        }
    }
    return urls;
}

fn main() -> Result<(), Box<dyn Error>> {
    let urls = get_samhita_urls();
    // Iterate over URLs
    for &ref url in urls.iter() {
        //println!("{url}");
        let kanda = url
            .split('/')
            .nth(11)
            .unwrap_or("-1")
            .parse::<i32>()
            .unwrap();
        let prasna = url
            .split('/')
            .last()
            .unwrap_or("-1.md")
            .trim_end_matches(".md")
            .parse::<i32>()
            .unwrap();

        // Fetch text from URL
        let text = get(url)?.text()?;

        // Parse verses
        let verses = parse_verses(&text);

        let mut parsed = HashMap::new();
        // Output each verse as JSON
        let mut anuvaka = 1;
        for verse in verses.iter() {
            let stripped = strip_index(verse);
            if !stripped.is_empty() {
                let json_output = json!({
                    "kanda": kanda,
                    "prasna": prasna,
                    "anuvaka": anuvaka,
                    "deva": strip_index(verse),
                });
                parsed.insert(format!("{}.{}.{}", kanda, prasna, anuvaka), json_output);
                anuvaka += 1;
            }
        }
        println!("PROCESSED {}.{}.{}", kanda, prasna, anuvaka);

        // Write JSON to file
        let mut file = File::create(format!("samhita/{kanda}.{prasna}.json"))?;
        file.write_all(serde_json::to_string_pretty(&parsed)?.as_bytes())?;
    }

    Ok(())
}

fn strip_index(input_string: &str) -> String {
    let pattern = r"\s*\[\d+\]\s*";
    let re = regex::Regex::new(pattern).unwrap();
    re.replace_all(input_string, "").to_string()
}

fn parse_verses(text: &str) -> Vec<String> {
    // Assuming each verse is separated by a newline
    text.lines().map(|line| line.trim().to_string()).collect()
}
