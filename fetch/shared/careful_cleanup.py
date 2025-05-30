#!/usr/bin/env python3
"""
CAREFUL cleanup of old directory structures.
SAFETY FIRST: Creates backups and validates before deletion.
"""

import shutil
import json
from pathlib import Path
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SafeCleanup:
    def __init__(self):
        self.backup_dir = Path(f"data/cleanup_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.primary_dir = Path("data/vedic_texts_by_sakha")
        self.dry_run = True
        
    def validate_primary_structure(self):
        """Validate that the primary structure is complete and correct."""
        logger.info("Validating primary structure...")
        
        if not self.primary_dir.exists():
            logger.error("Primary directory doesn't exist!")
            return False
            
        # Check for expected śākhās
        expected_sakhas = [
            "rigveda_शाकलशाखा",
            "samaveda_कौथुमशाखा", 
            "yajurveda_तैत्तिरीयशाखा",
            "atharvaveda_शौनकशाखा"
        ]
        
        missing_sakhas = []
        for sakha in expected_sakhas:
            sakha_dir = self.primary_dir / sakha
            if not sakha_dir.exists():
                missing_sakhas.append(sakha)
                
        if missing_sakhas:
            logger.error(f"Missing śākhās: {missing_sakhas}")
            return False
            
        # Validate that we have sources for each śākhā
        for sakha in expected_sakhas:
            sakha_dir = self.primary_dir / sakha
            sources = list(sakha_dir.iterdir())
            if len(sources) == 0:
                logger.error(f"No sources found for {sakha}")
                return False
            logger.info(f"✅ {sakha}: {len(sources)} sources")
            
        logger.info("✅ Primary structure validation passed")
        return True
        
    def identify_cleanup_targets(self):
        """Identify what can be safely cleaned up."""
        cleanup_targets = {
            "safe_to_remove": [],
            "backup_first": [],
            "keep": []
        }
        
        data_dir = Path("data")
        
        for item in data_dir.iterdir():
            if item.is_dir():
                item_name = item.name
                
                # Keep these important directories
                if item_name in ["vedic_texts_by_sakha", "taittiriya"]:
                    cleanup_targets["keep"].append(item)
                    
                # Archive directory is safe to remove (already archived)
                elif item_name == "vedanidhi_archive":
                    cleanup_targets["safe_to_remove"].append(item)
                    
                # Backup directories from reorganization
                elif item_name.startswith("vedanidhi_backup_"):
                    cleanup_targets["backup_first"].append(item)
                    
                # Original vedanidhi_complete (now superseded by organized structure)
                elif item_name == "vedanidhi_complete":
                    cleanup_targets["backup_first"].append(item)
                    
                # Old unified corpus (corrupted)
                elif item_name == "unified_corpus":
                    cleanup_targets["safe_to_remove"].append(item)
                    
                # Taittiriya backup
                elif item_name == "taittiriya_backup":
                    cleanup_targets["safe_to_remove"].append(item)
                    
                # Any other vedanidhi directories
                elif "vedanidhi" in item_name.lower():
                    cleanup_targets["backup_first"].append(item)
                    
                else:
                    cleanup_targets["keep"].append(item)
                    
        return cleanup_targets
        
    def create_safety_backup(self, targets):
        """Create backup of items before removal."""
        if not targets:
            return True
            
        logger.info(f"Creating safety backup at {self.backup_dir}...")
        
        if not self.dry_run:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
        for item in targets:
            backup_path = self.backup_dir / item.name
            logger.info(f"  Backing up: {item} -> {backup_path}")
            
            if not self.dry_run:
                if item.is_dir():
                    shutil.copytree(item, backup_path)
                else:
                    shutil.copy2(item, backup_path)
                    
        return True
        
    def execute_cleanup(self, targets):
        """Execute the cleanup."""
        logger.info("Executing cleanup...")
        
        for category, items in targets.items():
            if category == "keep":
                logger.info(f"KEEPING {len(items)} items:")
                for item in items:
                    logger.info(f"  ✅ Keep: {item}")
                    
            elif category == "safe_to_remove":
                logger.info(f"REMOVING {len(items)} safe items:")
                for item in items:
                    logger.info(f"  🗑️  Remove: {item}")
                    if not self.dry_run:
                        if item.exists():
                            shutil.rmtree(item)
                            
            elif category == "backup_first":
                logger.info(f"BACKUP+REMOVE {len(items)} items:")
                for item in items:
                    logger.info(f"  📦 Backup+Remove: {item}")
                    if not self.dry_run and item.exists():
                        shutil.rmtree(item)
                        
    def calculate_space_savings(self, targets):
        """Calculate how much space will be freed."""
        total_size = 0
        for category in ["safe_to_remove", "backup_first"]:
            for item in targets.get(category, []):
                if item.exists():
                    if item.is_dir():
                        size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
                    else:
                        size = item.stat().st_size
                    total_size += size
                    
        return total_size / (1024 * 1024)  # MB
        
    def run_cleanup(self, dry_run=True):
        """Run the complete cleanup process."""
        self.dry_run = dry_run
        
        logger.info("="*60)
        logger.info(f"SAFE CLEANUP ({'DRY RUN' if dry_run else 'EXECUTING'})")
        logger.info("="*60)
        
        # Step 1: Validate primary structure
        if not self.validate_primary_structure():
            logger.error("❌ Primary structure validation failed. Aborting cleanup.")
            return False
            
        # Step 2: Identify cleanup targets
        targets = self.identify_cleanup_targets()
        space_mb = self.calculate_space_savings(targets)
        
        logger.info(f"\nCleanup Plan:")
        logger.info(f"  Space to free: {space_mb:.1f} MB")
        logger.info(f"  Items to keep: {len(targets['keep'])}")
        logger.info(f"  Items to backup+remove: {len(targets['backup_first'])}")
        logger.info(f"  Items to remove: {len(targets['safe_to_remove'])}")
        
        # Step 3: Create safety backup
        if targets["backup_first"] and not dry_run:
            if not self.create_safety_backup(targets["backup_first"]):
                logger.error("❌ Backup creation failed. Aborting cleanup.")
                return False
                
        # Step 4: Execute cleanup
        self.execute_cleanup(targets)
        
        if dry_run:
            logger.info("\n" + "="*60)
            logger.info("DRY RUN COMPLETE. Review the plan above.")
            logger.info("To execute: python careful_cleanup.py --execute")
        else:
            logger.info("\n" + "="*60)
            logger.info("✅ CLEANUP COMPLETE!")
            logger.info(f"📦 Backup created at: {self.backup_dir}")
            logger.info(f"💾 Space freed: {space_mb:.1f} MB")
            
        return True

if __name__ == "__main__":
    import sys
    
    cleanup = SafeCleanup()
    execute = '--execute' in sys.argv
    
    success = cleanup.run_cleanup(dry_run=not execute)
    
    if not success:
        logger.error("Cleanup failed!")
        sys.exit(1)