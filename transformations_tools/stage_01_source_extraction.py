#!/usr/bin/env python3
"""
Stage 1: Source Extraction

Extracts text from DOCX and JSON source files, standardizing to common format.
Logs all operations for complete audit trail.
"""

import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import argparse

@dataclass
class ExtractedText:
    """Standardized extracted text with metadata"""
    text_id: str
    source_file: str
    raw_text: str
    hierarchy_hints: Dict[str, str]  # kanda, prapathaka, etc.
    metadata: Dict[str, str]
    extraction_timestamp: str
    quality_score: float

class TransformationLogger:
    """Logs all transformation operations"""
    
    def __init__(self, stage_name: str, output_dir: Path):
        self.stage = stage_name
        self.output_dir = Path(output_dir)
        self.log_file = self.output_dir / f"{stage_name}_log.json"
        self.operations = []
        
    def log_operation(self, action: str, details: Dict, status: str = "success"):
        operation = {
            "timestamp": datetime.now().isoformat(),
            "stage": self.stage,
            "action": action,
            "details": details,
            "status": status
        }
        self.operations.append(operation)
        print(f"[{self.stage}] {action}: {status}")
        
    def save_log(self):
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump({
                "transformation_log": {
                    "stage": self.stage,
                    "total_operations": len(self.operations),
                    "operations": self.operations
                }
            }, f, indent=2, ensure_ascii=False)

class DOCXExtractor:
    """Extract text from DOCX files (VedaVMS format)"""
    
    def __init__(self):
        # VedaVMS file naming patterns
        self.file_patterns = {
            'samhita': re.compile(r'TS (\d+) Baraha\.docx'),
            'pada': re.compile(r'TS (\d+)\.(\d+) Baraha Pada paatam\.docx'),
            'brahmana': re.compile(r'TB (\d+)\.(\d+)-(\d+)\.(\d+) Baraha\.docx'),
            'aranyaka': re.compile(r'TA (\d+)-(\d+) Baraha\.docx')
        }
        
    def extract_from_docx(self, docx_path: Path) -> ExtractedText:
        """Extract text from DOCX file"""
        
        # Determine text type and hierarchy from filename
        filename = docx_path.name
        text_type, hierarchy = self._parse_filename(filename)
        
        # Extract raw text from DOCX
        raw_text = self._extract_docx_text(docx_path)
        
        # Generate text ID
        text_id = self._generate_text_id(filename, hierarchy)
        
        # Calculate quality score
        quality_score = self._calculate_quality(raw_text)
        
        return ExtractedText(
            text_id=text_id,
            source_file=str(docx_path),
            raw_text=raw_text,
            hierarchy_hints=hierarchy,
            metadata={
                "source_type": "vedavms_docx",
                "text_type": text_type,
                "encoding": "baraha_south",
                "filename": filename
            },
            extraction_timestamp=datetime.now().isoformat(),
            quality_score=quality_score
        )
    
    def _parse_filename(self, filename: str) -> Tuple[str, Dict[str, str]]:
        """Parse VedaVMS filename to determine type and hierarchy"""
        
        for text_type, pattern in self.file_patterns.items():
            match = pattern.match(filename)
            if match:
                groups = match.groups()
                
                if text_type == 'samhita':
                    return text_type, {"kanda": groups[0]}
                elif text_type == 'pada':
                    return text_type, {"kanda": groups[0], "prapathaka": groups[1]}
                elif text_type == 'brahmana':
                    return text_type, {"kanda": groups[0], "start_prapathaka": groups[1], "end_prapathaka": groups[2]}
                elif text_type == 'aranyaka':
                    return text_type, {"start_prapathaka": groups[0], "end_prapathaka": groups[1]}
        
        return "unknown", {"filename": filename}
    
    def _extract_docx_text(self, docx_path: Path) -> str:
        """Extract raw text content from DOCX file"""
        
        text_content = []
        
        try:
            with zipfile.ZipFile(docx_path, 'r') as docx:
                # Read document.xml which contains the main text
                doc_xml = docx.read('word/document.xml')
                root = ET.fromstring(doc_xml)
                
                # Define namespace
                ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                
                # Extract all text elements
                for text_elem in root.findall('.//w:t', ns):
                    if text_elem.text:
                        text_content.append(text_elem.text)
        
        except Exception as e:
            raise Exception(f"Failed to extract text from {docx_path}: {e}")
        
        return ''.join(text_content)
    
    def _generate_text_id(self, filename: str, hierarchy: Dict[str, str]) -> str:
        """Generate standardized text ID"""
        
        # Base ID from filename
        base = filename.replace('.docx', '').replace(' ', '_').lower()
        
        # Add hierarchy info
        if 'kanda' in hierarchy:
            if 'prapathaka' in hierarchy:
                return f"ts_{hierarchy['kanda']}_{hierarchy['prapathaka']}_pada"
            else:
                return f"ts_{hierarchy['kanda']}_samhita"
        
        return f"vedavms_{base}"
    
    def _calculate_quality(self, text: str) -> float:
        """Calculate quality score based on content"""
        
        if not text or len(text) < 100:
            return 0.0
        
        # Check for accent marks (BarahaSouth Unicode)
        accent_count = text.count('\u0951') + text.count('\u0952')
        devanagari_chars = len(re.findall(r'[\u0900-\u097F]', text))
        
        if devanagari_chars == 0:
            return 0.0
        
        accent_ratio = accent_count / devanagari_chars
        base_score = min(accent_ratio * 2, 1.0)  # Expect good accent coverage
        
        # Bonus for reasonable length
        length_bonus = min(len(text) / 10000, 0.2)
        
        return min(base_score + length_bonus, 1.0)

class JSONExtractor:
    """Extract text from JSON files (Vedanidhi format)"""
    
    def extract_from_json(self, json_path: Path) -> List[ExtractedText]:
        """Extract text from Vedanidhi JSON file"""
        
        extracted_texts = []
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, list):
                # Array of text objects
                for i, item in enumerate(data):
                    extracted = self._process_json_item(item, json_path, i)
                    if extracted:
                        extracted_texts.append(extracted)
            elif isinstance(data, dict):
                # Single object or structured data
                extracted = self._process_json_item(data, json_path, 0)
                if extracted:
                    extracted_texts.append(extracted)
        
        except Exception as e:
            raise Exception(f"Failed to extract from {json_path}: {e}")
        
        return extracted_texts
    
    def _process_json_item(self, item: Dict, json_path: Path, index: int) -> Optional[ExtractedText]:
        """Process individual JSON item"""
        
        # Extract text content (flexible field names)
        text_fields = ['text', 'content', 'sanskrit', 'devanagari']
        raw_text = ""
        
        for field in text_fields:
            if field in item and item[field]:
                raw_text = str(item[field])
                break
        
        if not raw_text:
            return None
        
        # Generate text ID from filename and index
        filename = json_path.name.replace('.json', '')
        text_id = f"{filename}_{index:03d}" if index > 0 else filename
        
        # Extract hierarchy hints
        hierarchy = self._extract_hierarchy_hints(item, filename)
        
        # Calculate quality
        quality_score = self._calculate_json_quality(raw_text, item)
        
        return ExtractedText(
            text_id=text_id,
            source_file=str(json_path),
            raw_text=raw_text,
            hierarchy_hints=hierarchy,
            metadata={
                "source_type": "vedanidhi_json",
                "filename": json_path.name,
                "original_item": item
            },
            extraction_timestamp=datetime.now().isoformat(),
            quality_score=quality_score
        )
    
    def _extract_hierarchy_hints(self, item: Dict, filename: str) -> Dict[str, str]:
        """Extract hierarchy information from JSON item"""
        
        hierarchy = {}
        
        # Common hierarchy fields
        hierarchy_fields = ['kanda', 'mandala', 'sukta', 'rik', 'prapathaka', 'anuvaka', 'mantra']
        
        for field in hierarchy_fields:
            if field in item:
                hierarchy[field] = str(item[field])
        
        # Parse from filename if available
        filename_parts = filename.split('_')
        if len(filename_parts) >= 2:
            hierarchy['source_id'] = filename_parts[0]
        
        return hierarchy
    
    def _calculate_json_quality(self, text: str, item: Dict) -> float:
        """Calculate quality score for JSON text"""
        
        if not text or len(text) < 10:
            return 0.0
        
        # Check for accent marks
        accent_count = text.count('\u0951') + text.count('\u0952')
        devanagari_chars = len(re.findall(r'[\u0900-\u097F]', text))
        
        if devanagari_chars == 0:
            return 0.0
        
        accent_ratio = accent_count / devanagari_chars if devanagari_chars > 0 else 0
        base_score = min(accent_ratio * 2, 1.0)
        
        # Bonus for structured data
        structure_bonus = 0.1 if any(key in item for key in ['kanda', 'mandala', 'sukta']) else 0
        
        return min(base_score + structure_bonus, 1.0)

def extract_all_sources(source_dir: Path, output_dir: Path) -> Dict[str, List[ExtractedText]]:
    """Extract from all source files in directory"""
    
    logger = TransformationLogger("01_source_extraction", output_dir)
    
    docx_extractor = DOCXExtractor()
    json_extractor = JSONExtractor()
    
    all_extracted = {
        "docx": [],
        "json": []
    }
    
    # Process DOCX files
    docx_files = list(source_dir.glob("*.docx"))
    logger.log_operation("scan_docx_files", {"count": len(docx_files)})
    
    for docx_file in docx_files:
        try:
            extracted = docx_extractor.extract_from_docx(docx_file)
            all_extracted["docx"].append(extracted)
            logger.log_operation("extract_docx", {
                "file": docx_file.name,
                "text_id": extracted.text_id,
                "quality": extracted.quality_score,
                "text_length": len(extracted.raw_text)
            })
        except Exception as e:
            logger.log_operation("extract_docx", {
                "file": docx_file.name,
                "error": str(e)
            }, "error")
    
    # Process JSON files
    json_files = list(source_dir.glob("*.json"))
    logger.log_operation("scan_json_files", {"count": len(json_files)})
    
    for json_file in json_files:
        try:
            extracted_list = json_extractor.extract_from_json(json_file)
            all_extracted["json"].extend(extracted_list)
            logger.log_operation("extract_json", {
                "file": json_file.name,
                "texts_extracted": len(extracted_list),
                "avg_quality": sum(e.quality_score for e in extracted_list) / len(extracted_list) if extracted_list else 0
            })
        except Exception as e:
            logger.log_operation("extract_json", {
                "file": json_file.name,
                "error": str(e)
            }, "error")
    
    # Save extracted data
    output_file = output_dir / "extracted_texts.json"
    
    # Convert to serializable format
    serializable_data = {
        "extraction_summary": {
            "timestamp": datetime.now().isoformat(),
            "docx_files": len(all_extracted["docx"]),
            "json_files": len(all_extracted["json"]),
            "total_texts": len(all_extracted["docx"]) + len(all_extracted["json"])
        },
        "extracted_texts": []
    }
    
    for text_list in all_extracted.values():
        for text in text_list:
            serializable_data["extracted_texts"].append({
                "text_id": text.text_id,
                "source_file": text.source_file,
                "raw_text": text.raw_text,
                "hierarchy_hints": text.hierarchy_hints,
                "metadata": text.metadata,
                "extraction_timestamp": text.extraction_timestamp,
                "quality_score": text.quality_score
            })
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(serializable_data, f, indent=2, ensure_ascii=False)
    
    logger.log_operation("save_extracted_data", {
        "output_file": str(output_file),
        "total_texts": len(serializable_data["extracted_texts"])
    })
    
    logger.save_log()
    
    return all_extracted

def main():
    parser = argparse.ArgumentParser(description='Extract text from source files')
    parser.add_argument('source_dir', help='Directory containing source files')
    parser.add_argument('output_dir', help='Output directory for extracted data')
    
    args = parser.parse_args()
    
    source_dir = Path(args.source_dir)
    output_dir = Path(args.output_dir)
    
    if not source_dir.exists():
        print(f"Error: Source directory {source_dir} does not exist")
        return
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Extracting from {source_dir} to {output_dir}")
    
    extracted = extract_all_sources(source_dir, output_dir)
    
    total_texts = sum(len(texts) for texts in extracted.values())
    print(f"Extraction complete: {total_texts} texts extracted")

if __name__ == "__main__":
    main()