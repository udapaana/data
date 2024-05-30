use reqwest::blocking::get;
use serde_json::json;
use std::error::Error;
use std::fs::File;
use std::io::Write;


let template = "https://raw.githubusercontent.com/udapaana/raw_etexts/master/vedaH/yajur/taittirIya/mUlam/saMhitA/1/1.md";

let stubs = vec![
    (1,1),(1,2),(1,3),(1,4),(1,5),(1,6),(1,7),
    (2,1),(2,2),(2,3),(2,4),(2,5),(2,6),
    
]
        
fn main() -> Result<(), Box<dyn Error>> {

    // Iterate over URLs
    for (file_index, &url) in urls.iter().enumerate() {
        let kanda = url.split('/').nth(11).unwrap_or("").parse::<i32>().unwrap();
        let prasna = url.split('/').last().unwrap_or("").trim_end_matches(".md").parse::<i32>().unwrap();

        // Fetch text from URL
        let text = get(url)?.text()?;

        // Parse verses
        let verses = parse_verses(&text);

        let mut parsed = Vec::new();
        // Output each verse as JSON
        let mut index = 1;
        for verse in verses.iter() {
            let stripped = strip_index(verse);
            if !stripped.is_empty(){
                let json_output = json!({
                    "kanda": kanda,
                    "prasna": prasna,
                    "anuvaka": index,
                    "deva": strip_index(verse),
                });
                parsed.push(json_output);
                index+=1;
            }
        }

        // Write JSON to file
        let mut file = File::create(format!("outputs/{}.json", file_index))?;
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

