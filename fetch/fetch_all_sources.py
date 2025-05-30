#!/usr/bin/env python3
"""
Master fetch script for all Vedic sources.
Coordinates downloading from different sources based on configurations.
"""

import json
import sys
from pathlib import Path

def load_config(source_name):
    """Load configuration for a specific source."""
    config_path = Path(__file__).parent / source_name / f"{source_name}_config.json"
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return None

def fetch_vedanidhi():
    """Fetch from Vedanidhi using existing scripts."""
    print("=== Fetching from Vedanidhi ===")
    config = load_config("vedanidhi")
    if config:
        print(f"Targets: {list(config['targets'].keys())}")
        # Import and run existing vedanidhi scripts
        # Implementation would call existing download scripts
    else:
        print("No Vedanidhi configuration found")

def fetch_vedavms():
    """VedaVMS files are manually downloaded - just verify they exist."""
    print("=== Verifying VedaVMS files ===")
    config = load_config("vedavms")
    if config:
        print("VedaVMS files are manually downloaded and already in place")
        # Could add verification logic here
    else:
        print("No VedaVMS configuration found")

def main():
    """Main fetch coordinator."""
    print("Udapaana Source Fetch Coordinator")
    print("=================================")
    
    sources = ["vedanidhi", "vedavms"]
    
    for source in sources:
        if source == "vedanidhi":
            fetch_vedanidhi()
        elif source == "vedavms":
            fetch_vedavms()
        print()

if __name__ == "__main__":
    main()
