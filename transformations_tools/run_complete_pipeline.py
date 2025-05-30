#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path
import time
from datetime import datetime

def run_stage(script_name: str, stage_name: str) -> bool:
    """Run a pipeline stage and return success status"""
    print(f"\n{'=' * 60}")
    print(f"RUNNING {stage_name}")
    print(f"{'=' * 60}")
    print(f"Script: {script_name}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = time.time()
    
    try:
        # Run the stage script
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Print output
        if result.stdout:
            print("\nOutput:")
            print(result.stdout)
        
        if result.stderr:
            print("\nWarnings/Errors:")
            print(result.stderr)
        
        elapsed = time.time() - start_time
        print(f"\n✓ {stage_name} completed in {elapsed:.1f} seconds")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n✗ {stage_name} failed with exit code {e.returncode}")
        if e.stdout:
            print("\nOutput:")
            print(e.stdout)
        if e.stderr:
            print("\nError:")
            print(e.stderr)
        return False
    except Exception as e:
        print(f"\n✗ {stage_name} failed with error: {e}")
        return False

def main():
    """Run the complete transformation pipeline"""
    print("=" * 80)
    print("VEDIC TEXT TRANSFORMATION PIPELINE (UVTS)")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Define pipeline stages
    stages = [
        ("stage_01_source_extraction.py", "STAGE 1: SOURCE EXTRACTION"),
        ("stage_02_text_normalization.py", "STAGE 2: TEXT NORMALIZATION"),
        ("stage_03_accent_standardization.py", "STAGE 3: ACCENT STANDARDIZATION (UVTS)"),
        ("create_vedic_database.py", "DATABASE CREATION")
    ]
    
    # Track results
    results = []
    total_start = time.time()
    
    # Run each stage
    for script, stage_name in stages:
        success = run_stage(script, stage_name)
        results.append((stage_name, success))
        
        if not success:
            print(f"\n⚠️  Pipeline stopped due to failure in {stage_name}")
            break
        
        # Small delay between stages
        time.sleep(1)
    
    # Print summary
    total_elapsed = time.time() - total_start
    
    print("\n" + "=" * 80)
    print("PIPELINE SUMMARY")
    print("=" * 80)
    
    for stage_name, success in results:
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{stage_name}: {status}")
    
    successful = sum(1 for _, success in results if success)
    print(f"\nStages completed: {successful}/{len(stages)}")
    print(f"Total time: {total_elapsed:.1f} seconds")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if database was created
    db_path = Path(__file__).parent.parent / "vedic_corpus_uvts.sqlite"
    if db_path.exists():
        print(f"\n✓ Database created: {db_path}")
        print(f"  Size: {db_path.stat().st_size / 1024 / 1024:.2f} MB")
    else:
        print(f"\n✗ Database not found at: {db_path}")
    
    # Return exit code
    return 0 if successful == len(stages) else 1

if __name__ == "__main__":
    sys.exit(main())