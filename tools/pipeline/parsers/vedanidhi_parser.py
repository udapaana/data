"""
Vedanidhi JSON Parser
Extracts text from Devanagari JSON files downloaded from vedanidhi.org API
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re
import logging

logger = logging.getLogger(__name__)

class VedanidhiParser:
    """Parser for Vedanidhi JSON API response files."""
    
    def __init__(self):
        self.source_name = "vedanidhi"
        self.encoding = "devanagari"
        
        # Mapping of Vedanidhi codes to our schema
        self.veda_mapping = {
            '01': 'rigveda',
            '02': 'yajurveda', 
            '03': 'samaveda',
            '04': 'atharvaveda'
        }
        
        self.sakha_mapping = {
            '01': 'shakala',      # Rigveda
            '02': 'bashkala',     # Rigveda (if present)
            '03': 'kauthuma',     # Samaveda
            '04': 'taittiriya',   # Yajurveda
            '05': 'shaunaka'      # Atharvaveda
        }
        
        self.text_type_mapping = {
            '01': 'samhita',
            '02': 'brahmana',
            '03': 'aranyaka', 
            '04': 'upanishad'
        }
    
    def parse_file(self, file_path: str) -> Dict:
        """
        Parse a Vedanidhi JSON file and extract structured text.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Dict with extracted text and metadata
        """
        file_path = Path(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract metadata from filename and content
            metadata = self._parse_filename(file_path.name)
            content_metadata = self._extract_metadata(data)
            metadata.update(content_metadata)
            
            # Extract text content
            text_content = self._extract_text(data)
            
            # Parse structure from content
            structure = self._parse_structure(data, metadata)
            
            result = {
                'source_file': str(file_path),
                'source_name': self.source_name,
                'encoding': self.encoding,
                'metadata': metadata,
                'raw_text': text_content,
                'structure': structure,
                'extraction_method': 'json-parse',
                'file_size': file_path.stat().st_size,
                'file_modified': file_path.stat().st_mtime,
                'json_data': data  # Preserve original for debugging
            }
            
            logger.info(f"Successfully parsed {file_path.name}: {len(text_content)} characters")
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            raise
    
    def _parse_filename(self, filename: str) -> Dict:
        """Extract metadata from Vedanidhi filename patterns."""
        metadata = {
            'original_filename': filename
        }
        
        # Parse filename patterns like: 01010102_शाकलसंहिता_-_(01010102)_अष्टकम्.json
        # Format: VVSSTTNN_title_-_(VVSSTTNN)_subdivision.json
        match = re.search(r'^(\d{2})(\d{2})(\d{2})(\d{2})_(.+?)_-_\(\1\2\3\4\)_(.+?)\.json$', filename)
        
        if match:
            veda_code = match.group(1)
            sakha_code = match.group(2) 
            text_type_code = match.group(3)
            section_code = match.group(4)
            title = match.group(5)
            subdivision = match.group(6)
            
            metadata.update({
                'veda_code': veda_code,
                'sakha_code': sakha_code,
                'text_type_code': text_type_code,
                'section_code': section_code,
                'title': title,
                'subdivision': subdivision,
                'veda': self.veda_mapping.get(veda_code, 'unknown'),
                'text_type': self.text_type_mapping.get(text_type_code, 'unknown')
            })
            
            # Map sakha based on veda
            if veda_code == '01':  # Rigveda
                metadata['sakha'] = 'shakala'
            elif veda_code == '02':  # Yajurveda  
                metadata['sakha'] = 'taittiriya'
            elif veda_code == '03':  # Samaveda
                metadata['sakha'] = 'kauthuma'
            elif veda_code == '04':  # Atharvaveda
                metadata['sakha'] = 'shaunaka'
                
        else:
            # Try simpler patterns
            simple_match = re.search(r'^(\d{6})_(.+?)\.json$', filename)
            if simple_match:
                code = simple_match.group(1)
                title = simple_match.group(2)
                
                if len(code) >= 6:
                    veda_code = code[:2]
                    sakha_code = code[2:4]
                    text_type_code = code[4:6]
                    
                    metadata.update({
                        'veda_code': veda_code,
                        'sakha_code': sakha_code,
                        'text_type_code': text_type_code,
                        'title': title,
                        'veda': self.veda_mapping.get(veda_code, 'unknown'),
                        'text_type': self.text_type_mapping.get(text_type_code, 'unknown')
                    })
        
        return metadata
    
    def _extract_metadata(self, data: Dict) -> Dict:
        """Extract metadata from JSON content structure."""
        metadata = {}
        
        # Look for metadata fields in the JSON
        if isinstance(data, dict):
            for key in ['title', 'name', 'description', 'author', 'source']:
                if key in data:
                    metadata[f'content_{key}'] = data[key]
        
        return metadata
    
    def _extract_text(self, data: any) -> str:
        """Recursively extract text content from JSON structure."""
        text_parts = []
        
        if isinstance(data, str):
            # Clean and normalize the text
            text = data.strip()
            if text and not text.isdigit():  # Skip pure numbers
                text_parts.append(text)
                
        elif isinstance(data, dict):
            # Process dictionary values
            for key, value in data.items():
                if key.lower() in ['text', 'content', 'verse', 'mantra', 'pada']:
                    # These keys likely contain the main text
                    text_parts.append(self._extract_text(value))
                elif not key.lower() in ['id', 'number', 'index', 'count']:
                    # Skip metadata keys, process others
                    text_parts.append(self._extract_text(value))
                    
        elif isinstance(data, list):
            # Process list items
            for item in data:
                text_parts.append(self._extract_text(item))
        
        # Join and clean the result
        result = '\n'.join(filter(None, text_parts))
        return result
    
    def _parse_structure(self, data: any, metadata: Dict) -> Dict:
        """Parse hierarchical structure from JSON data."""
        structure = {
            'veda': metadata.get('veda'),
            'sakha': metadata.get('sakha'),
            'text_type': metadata.get('text_type'),
            'sections': []
        }
        
        # Try to identify structural elements
        if isinstance(data, dict):
            # Look for hierarchical markers
            for key, value in data.items():
                if key.lower() in ['kanda', 'ashtaka', 'mandala', 'adhyaya', 'sukta', 'mantra']:
                    structure[key.lower()] = value
                elif key.lower() in ['sections', 'chapters', 'verses']:
                    if isinstance(value, list):
                        structure['sections'] = self._parse_sections(value)
        
        elif isinstance(data, list):
            # Treat as a list of sections
            structure['sections'] = self._parse_sections(data)
        
        return structure
    
    def _parse_sections(self, sections: List) -> List[Dict]:
        """Parse individual sections from a list."""
        parsed_sections = []
        
        for i, section in enumerate(sections):
            section_data = {
                'index': i,
                'content': self._extract_text(section)
            }
            
            # Try to extract section metadata
            if isinstance(section, dict):
                for key in ['number', 'id', 'title', 'verse_number']:
                    if key in section:
                        section_data[key] = section[key]
            
            if section_data['content'].strip():
                parsed_sections.append(section_data)
        
        return parsed_sections
    
    def get_file_list(self, base_path: str) -> List[str]:
        """Get list of Vedanidhi JSON files to process."""
        base_path = Path(base_path)
        json_files = []
        
        # Find all JSON files in Vedanidhi directories
        for vedanidhi_dir in base_path.glob('**/vedanidhi/*/source'):
            for json_file in vedanidhi_dir.glob('*.json'):
                json_files.append(str(json_file))
        
        return sorted(json_files)
    
    def validate_file(self, file_path: str) -> bool:
        """Validate that file can be processed."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return False
            
        if file_path.suffix.lower() != '.json':
            logger.error(f"Not a JSON file: {file_path}")
            return False
            
        try:
            # Try to parse the JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
            return True
        except Exception as e:
            logger.error(f"Cannot parse JSON file {file_path}: {e}")
            return False


if __name__ == "__main__":
    # Test the parser
    parser = VedanidhiParser()
    
    # Find test files
    base_path = "/Users/skmnktl/Projects/udapaana/data/vedic_texts"
    files = parser.get_file_list(base_path)
    
    print(f"Found {len(files)} Vedanidhi JSON files:")
    for file_path in files[:5]:  # Show first 5
        print(f"  {Path(file_path).name}")
        
        if parser.validate_file(file_path):
            try:
                result = parser.parse_file(file_path)
                print(f"    ✓ Parsed: {len(result['raw_text'])} chars")
                print(f"    Metadata: {result['metadata']}")
            except Exception as e:
                print(f"    ✗ Error: {e}")
        else:
            print(f"    ✗ Validation failed")
        print()