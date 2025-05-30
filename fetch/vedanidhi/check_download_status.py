#!/usr/bin/env python3
"""Check the status of the Vedanidhi download."""

import json
from pathlib import Path

def check_status():
    """Check and display download status."""
    progress_file = Path("data/vedanidhi_complete/download_progress.json")
    
    if not progress_file.exists():
        print("No download progress found.")
        return
    
    with open(progress_file) as f:
        progress = json.load(f)
    
    completed = len(progress.get('completed', []))
    failed = len(progress.get('failed', []))
    total = 107
    remaining = total - completed - failed
    
    print(f"Vedanidhi Download Status")
    print(f"=" * 40)
    print(f"Total sources: {total}")
    print(f"Completed: {completed} ({completed/total*100:.1f}%)")
    print(f"Failed: {failed} ({failed/total*100:.1f}%)")
    print(f"Remaining: {remaining} ({remaining/total*100:.1f}%)")
    print(f"Last index: {progress.get('last_index', 0)}")
    
    if failed > 0:
        print(f"\nFailed sources ({failed}):")
        for source_id in progress['failed'][:10]:
            print(f"  - {source_id}")
        if failed > 10:
            print(f"  ... and {failed - 10} more")
    
    # Check download directory
    download_dir = Path("data/vedanidhi_complete")
    if download_dir.exists():
        json_files = list(download_dir.glob("**/*.json"))
        json_files = [f for f in json_files if "validation_failures" not in str(f) and f.name != "download_progress.json"]
        
        print(f"\nDownloaded files: {len(json_files)}")
        
        # Calculate total size
        total_size = sum(f.stat().st_size for f in json_files) / (1024 * 1024)  # MB
        print(f"Total size: {total_size:.1f} MB")
        
        # Show Veda breakdown
        veda_counts = {}
        for f in json_files:
            veda = f.parent.name
            veda_counts[veda] = veda_counts.get(veda, 0) + 1
        
        print("\nBy Veda:")
        for veda, count in sorted(veda_counts.items()):
            print(f"  {veda}: {count} files")

if __name__ == "__main__":
    check_status()