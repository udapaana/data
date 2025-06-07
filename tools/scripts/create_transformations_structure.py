#!/usr/bin/env python3

import os
from pathlib import Path
import json

def create_transformations_structure():
    """
    Create the transformations directory structure for each śākhā source.
    Transformations sit at same level as source/ and parsed/ directories.
    """
    
    base_path = Path("/Users/skmnktl/Projects/udapaana/data/vedic_texts")
    
    print("=== CREATING TRANSFORMATIONS ARCHITECTURE ===\n")
    
    # Find all source directories
    source_dirs = []
    for source_dir in base_path.rglob("source"):
        if source_dir.is_dir():
            source_dirs.append(source_dir)
    
    created_count = 0
    
    for source_dir in source_dirs:
        # Get parent directory (should be at text_type level)
        text_type_dir = source_dir.parent
        transformations_dir = text_type_dir / "transformations"
        
        if not transformations_dir.exists():
            transformations_dir.mkdir()
            print(f"Created: {transformations_dir.relative_to(base_path)}")
            created_count += 1
            
            # Create transformation pipeline structure
            pipeline_dirs = [
                "01_source_extraction",    # Extract from DOCX/JSON
                "02_text_normalization",   # Clean and normalize text
                "03_accent_standardization", # Convert to EBA format
                "04_structure_mapping",    # Map to śākhā hierarchy
                "05_cross_references",     # Add internal references
                "06_validation",           # Quality checks
                "07_final_format"          # Ready for parsed/
            ]
            
            for pipeline_dir in pipeline_dirs:
                (transformations_dir / pipeline_dir).mkdir()
            
            # Create transformation manifest
            manifest = {
                "transformation_pipeline": {
                    "version": "1.0",
                    "created": "2025-05-29",
                    "description": "Iterative transformation pipeline with complete logging"
                },
                "pipeline_stages": [
                    {
                        "stage": "01_source_extraction",
                        "description": "Extract raw text from source files (DOCX/JSON)",
                        "input": "source/ directory files",
                        "output": "extracted_text.json, extraction_log.json",
                        "tools": ["docx_parser", "json_extractor"],
                        "validation": ["encoding_check", "completeness_check"]
                    },
                    {
                        "stage": "02_text_normalization", 
                        "description": "Normalize Unicode, clean formatting, standardize punctuation",
                        "input": "01_source_extraction/extracted_text.json",
                        "output": "normalized_text.json, normalization_log.json",
                        "tools": ["unicode_normalizer", "text_cleaner"],
                        "validation": ["character_set_check", "consistency_check"]
                    },
                    {
                        "stage": "03_accent_standardization",
                        "description": "Convert accent marks to Extended Baraha ASCII format",
                        "input": "02_text_normalization/normalized_text.json", 
                        "output": "eba_text.json, accent_conversion_log.json",
                        "tools": ["eba_converter", "accent_mapper"],
                        "validation": ["accent_coverage_check", "round_trip_test"]
                    },
                    {
                        "stage": "04_structure_mapping",
                        "description": "Map to śākhā-specific hierarchical structure",
                        "input": "03_accent_standardization/eba_text.json",
                        "output": "structured_text.json, structure_mapping_log.json", 
                        "tools": ["hierarchy_mapper", "metadata_extractor"],
                        "validation": ["structure_completeness", "hierarchy_consistency"]
                    },
                    {
                        "stage": "05_cross_references",
                        "description": "Add internal cross-references and parallel passages",
                        "input": "04_structure_mapping/structured_text.json",
                        "output": "cross_referenced_text.json, cross_ref_log.json",
                        "tools": ["reference_detector", "parallel_finder"],
                        "validation": ["reference_validity", "link_integrity"]
                    },
                    {
                        "stage": "06_validation",
                        "description": "Final quality validation and scholar review",
                        "input": "05_cross_references/cross_referenced_text.json",
                        "output": "validated_text.json, validation_report.json",
                        "tools": ["quality_validator", "scholar_review"],
                        "validation": ["complete_pipeline_check", "accuracy_metrics"]
                    },
                    {
                        "stage": "07_final_format",
                        "description": "Generate final format for parsed/ directory",
                        "input": "06_validation/validated_text.json",
                        "output": "final_corpus.json, transformation_summary.json",
                        "tools": ["format_generator", "metadata_compiler"], 
                        "validation": ["format_compliance", "completeness_final"]
                    }
                ],
                "logging_standards": {
                    "log_format": "JSON with timestamp, stage, action, input, output, status",
                    "error_handling": "Continue pipeline with error flagging",
                    "rollback_support": "Each stage can be reverted independently",
                    "audit_trail": "Complete provenance from source to final"
                }
            }
            
            with open(transformations_dir / "transformation_manifest.json", 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
        else:
            print(f"Exists: {transformations_dir.relative_to(base_path)}")
    
    # Create shared transformation utilities
    shared_tools_dir = base_path.parent / "transformations_tools"
    if not shared_tools_dir.exists():
        shared_tools_dir.mkdir()
        print(f"\nCreated shared tools: {shared_tools_dir}")
        
        # Create tool templates
        tools = [
            "eba_converter.py",
            "docx_parser.py", 
            "json_extractor.py",
            "unicode_normalizer.py",
            "text_cleaner.py",
            "accent_mapper.py",
            "hierarchy_mapper.py",
            "metadata_extractor.py",
            "reference_detector.py",
            "parallel_finder.py",
            "quality_validator.py",
            "format_generator.py",
            "transformation_logger.py"
        ]
        
        for tool in tools:
            tool_path = shared_tools_dir / tool
            with open(tool_path, 'w') as f:
                tool_content = f'''#!/usr/bin/env python3
"""
{tool} - Transformation tool for Vedic text processing

Part of the Udapaana transformation pipeline.
Each tool logs all operations for complete audit trail.
"""

import json
import logging
from pathlib import Path
from datetime import datetime

class TransformationLogger:
    def __init__(self, stage_name, input_file, output_dir):
        self.stage = stage_name
        self.input_file = input_file
        self.output_dir = Path(output_dir)
        self.log_file = self.output_dir / f"{{stage_name}}_log.json"
        self.operations = []
        
    def log_operation(self, action, details, status="success"):
        operation = {{
            "timestamp": datetime.now().isoformat(),
            "stage": self.stage,
            "action": action,
            "details": details,
            "status": status,
            "input_file": str(self.input_file)
        }}
        self.operations.append(operation)
        
    def save_log(self):
        with open(self.log_file, 'w') as f:
            json.dump({{
                "transformation_log": {{
                    "stage": self.stage,
                    "total_operations": len(self.operations),
                    "operations": self.operations
                }}
            }}, f, indent=2)

# Tool-specific implementation goes here
def main():
    print(f"Running {tool}")
    # Implementation placeholder
    pass

if __name__ == "__main__":
    main()
'''
                f.write(tool_content)
    
    print(f"\n=== TRANSFORMATIONS ARCHITECTURE CREATED ===")
    print(f"Created transformations directories: {created_count}")
    print(f"Pipeline stages: 7 (01_source_extraction → 07_final_format)")
    print(f"Shared tools created: {len(tools)}")
    print(f"")
    print(f"STRUCTURE:")
    print(f"  data/vedic_texts/{'{veda}'}/{'{sakha}'}/{'{source}'}/{'{text_type}'}/")
    print(f"    source/           - Original files") 
    print(f"    transformations/  - Pipeline with complete logging")
    print(f"    parsed/           - Final processed output")
    print(f"    scripts/          - Processing scripts")
    print(f"")
    print(f"  data/transformations_tools/ - Shared transformation utilities")

if __name__ == "__main__":
    create_transformations_structure()