#!/usr/bin/env python3
"""
Resume parsing script - can be used to restart parsing from where it left off.
"""

import json
from robust_parser import RobustTaittiriyaParser

def show_checkpoint_status():
    """Show the current checkpoint status."""
    parser = RobustTaittiriyaParser("/Users/skmnktl/Projects/udapaana/data/taittiriya")
    checkpoint = parser.load_checkpoint()
    
    print("=== Checkpoint Status ===")
    print(f"Completed files: {len(checkpoint.get('completed_files', []))}")
    print(f"Current file: {checkpoint.get('current_file', 'None')}")
    print(f"Samhita processed: {checkpoint.get('samhita_processed', False)}")
    
    completed = set(checkpoint.get('completed_files', []))
    all_files = set([f.name for f in parser.padam_dir.glob("*.docx")])
    remaining = all_files - completed
    
    print(f"\nRemaining files: {len(remaining)}")
    for file in sorted(remaining):
        print(f"  - {file}")
    
    if completed:
        print(f"\nCompleted files: {len(completed)}")
        for file in sorted(completed):
            print(f"  - {file}")

def resume_parsing():
    """Resume parsing from checkpoint."""
    parser = RobustTaittiriyaParser("/Users/skmnktl/Projects/udapaana/data/taittiriya")
    print("Resuming parsing from checkpoint...")
    parser.process_all_files()

def main():
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        show_checkpoint_status()
    else:
        resume_parsing()

if __name__ == "__main__":
    main()