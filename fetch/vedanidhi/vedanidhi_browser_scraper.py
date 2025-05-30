#!/usr/bin/env python3
"""
Vedanidhi Browser-Based Scraper
Uses Selenium to navigate the site and extract data properly
"""

import json
import time
import os
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import logging

class VedanidhiBrowserScraper:
    def __init__(self, headless=True):
        self.base_url = "https://vaakya.vedanidhi.in/vedanidhi"
        self.download_dir = Path("data/vedanidhi_browser_scraped")
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)
        
        # Setup Chrome options
        self.chrome_options = Options()
        if headless:
            self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        
    def start_browser(self):
        """Start the browser session"""
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        
    def navigate_to_texts(self, veda_code, shakha_code, text_code):
        """Navigate to specific texts using the browse interface"""
        # Build the browse URL
        browse_url = f"{self.base_url}/browse.htm?lang=dv&vedam={veda_code}&shakha={shakha_code}&text={text_code}"
        
        self.logger.info(f"Navigating to: {browse_url}")
        self.driver.get(browse_url)
        
        # Wait for the page to load
        time.sleep(3)
        
    def extract_table_data(self):
        """Extract data from the DataTables table"""
        try:
            # Wait for the table to be present
            table = self.wait.until(
                EC.presence_of_element_located((By.ID, "datatable"))
            )
            
            # Get all rows
            rows = table.find_elements(By.TAG_NAME, "tr")
            
            data = []
            for row in rows[1:]:  # Skip header row
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 3:
                    # Extract text from each cell
                    location = cells[0].text.strip()
                    text = cells[1].text.strip()
                    
                    data.append({
                        "location": location,
                        "text": text
                    })
            
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to extract table data: {e}")
            return []
    
    def check_pagination(self):
        """Check if there are more pages"""
        try:
            # Look for pagination info
            info = self.driver.find_element(By.CLASS_NAME, "dataTables_info")
            if info:
                text = info.text
                # Parse "Showing 1 to 10 of 1,234 entries"
                import re
                match = re.search(r'of ([\d,]+) entries', text)
                if match:
                    total = int(match.group(1).replace(',', ''))
                    return total > 10  # Assuming 10 per page
            return False
        except:
            return False
    
    def click_next_page(self):
        """Click the next page button"""
        try:
            next_btn = self.driver.find_element(By.CLASS_NAME, "paginate_button.next")
            if "disabled" not in next_btn.get_attribute("class"):
                next_btn.click()
                time.sleep(2)  # Wait for page to load
                return True
            return False
        except:
            return False
    
    def scrape_texts(self, veda_code, shakha_code, text_code, veda_name, shakha_name, text_type):
        """Scrape all texts for a given category"""
        self.logger.info(f"Scraping {veda_name} > {shakha_name} > {text_type}")
        
        # Navigate to the page
        self.navigate_to_texts(veda_code, shakha_code, text_code)
        
        all_data = []
        page_num = 1
        
        while True:
            self.logger.info(f"  Extracting page {page_num}")
            
            # Extract data from current page
            page_data = self.extract_table_data()
            if not page_data:
                self.logger.warning("  No data found on page")
                break
                
            all_data.extend(page_data)
            self.logger.info(f"  Found {len(page_data)} items")
            
            # Check if there are more pages
            if not self.click_next_page():
                break
                
            page_num += 1
            
        # Save the data
        if all_data:
            save_dir = self.download_dir / veda_name / shakha_name / text_type
            save_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"scraped_data.json"
            filepath = save_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    "veda": veda_name,
                    "shakha": shakha_name,
                    "text_type": text_type,
                    "total_items": len(all_data),
                    "scraped_at": datetime.now().isoformat(),
                    "data": all_data
                }, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Saved {len(all_data)} items to {filepath}")
        
        return len(all_data)
    
    def scrape_all(self):
        """Scrape all target texts"""
        # Start browser
        self.start_browser()
        
        try:
            # Test with a small set first
            test_targets = [
                # Rigveda
                ("01", "0101", "010101", "rigveda", "shakala", "samhita"),
                
                # Yajurveda - Krishna
                ("02", "0201", "020101", "yajurveda", "taittiriya", "samhita"),
                
                # Samaveda
                ("03", "0301", "030101", "samaveda", "kauthuma", "samhita"),
                
                # Atharvaveda
                ("04", "0401", "040101", "atharvaveda", "shaunaka", "samhita"),
            ]
            
            total_scraped = 0
            
            for veda_code, shakha_code, text_code, veda_name, shakha_name, text_type in test_targets:
                try:
                    count = self.scrape_texts(veda_code, shakha_code, text_code, 
                                            veda_name, shakha_name, text_type)
                    total_scraped += count
                    
                    # Be respectful - wait between different texts
                    time.sleep(5)
                    
                except Exception as e:
                    self.logger.error(f"Failed to scrape {veda_name}/{shakha_name}/{text_type}: {e}")
                    continue
            
            self.logger.info(f"\nTotal items scraped: {total_scraped}")
            
        finally:
            # Close browser
            self.driver.quit()

def main():
    # Check if Selenium and Chrome driver are available
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        print("Selenium is installed")
    except ImportError:
        print("Please install selenium: pip install selenium")
        print("Also ensure you have Chrome and chromedriver installed")
        return
    
    scraper = VedanidhiBrowserScraper(headless=False)  # Run with GUI for testing
    scraper.scrape_all()

if __name__ == "__main__":
    main()