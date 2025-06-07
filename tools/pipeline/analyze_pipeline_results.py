#!/usr/bin/env python3
"""
Analysis and validation script for enhanced udapaana pipeline results.

This script analyzes the results of the enhanced pipeline processing:
1. Round-trip testing validation
2. Pattern discovery analysis
3. Quality metrics by source/sakha/veda
4. Comprehensive reporting
"""

import sqlite3
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UdapaanaPipelineAnalyzer:
    """Analyzer for enhanced udapaana pipeline results."""
    
    def __init__(self, db_path: str = "udapaana_enhanced.sqlite"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
    
    def analyze_all(self, output_dir: Path = None):
        """Run complete analysis and generate reports."""
        if output_dir is None:
            output_dir = Path("pipeline_analysis_results")
        
        output_dir.mkdir(exist_ok=True)
        
        logger.info("Starting comprehensive pipeline analysis...")
        
        # 1. Overall statistics
        overall_stats = self.get_overall_statistics()
        self.save_json_report(overall_stats, output_dir / "overall_statistics.json")
        
        # 2. Round-trip testing analysis
        round_trip_analysis = self.analyze_round_trip_results()
        self.save_json_report(round_trip_analysis, output_dir / "round_trip_analysis.json")
        
        # 3. Pattern discovery analysis
        pattern_analysis = self.analyze_discovered_patterns()
        self.save_json_report(pattern_analysis, output_dir / "pattern_discovery_analysis.json")
        
        # 4. Quality metrics by source
        quality_by_source = self.analyze_quality_by_source()
        self.save_json_report(quality_by_source, output_dir / "quality_by_source.json")
        
        # 5. Source detection analysis
        detection_analysis = self.analyze_source_detection()
        self.save_json_report(detection_analysis, output_dir / "source_detection_analysis.json")
        
        # 6. Generate visualizations
        self.generate_visualizations(output_dir)
        
        # 7. Generate comprehensive report
        self.generate_comprehensive_report(output_dir)
        
        logger.info(f"Analysis completed. Results saved to {output_dir}")
    
    def get_overall_statistics(self) -> Dict[str, Any]:
        """Get overall pipeline statistics."""
        stats = {}
        
        # Basic counts
        cursor = self.conn.execute("SELECT COUNT(*) as count FROM texts")
        stats['total_texts'] = cursor.fetchone()['count']
        
        cursor = self.conn.execute("SELECT COUNT(*) as count FROM text_lines")
        stats['total_lines'] = cursor.fetchone()['count']
        
        cursor = self.conn.execute("SELECT COUNT(*) as count FROM discovered_patterns")
        stats['total_patterns'] = cursor.fetchone()['count']
        
        # Round-trip success rates
        cursor = self.conn.execute("""
            SELECT 
                COUNT(*) as total_lines,
                SUM(CASE WHEN round_trip_valid THEN 1 ELSE 0 END) as successful_lines,
                AVG(confidence_score) as avg_confidence
            FROM text_lines
        """)
        row = cursor.fetchone()
        stats['round_trip_success_rate'] = row['successful_lines'] / row['total_lines'] if row['total_lines'] > 0 else 0
        stats['average_confidence'] = row['avg_confidence']
        
        # Processing overview
        cursor = self.conn.execute("""
            SELECT run_id, processing_start_time, processing_end_time, 
                   total_processing_time_seconds, round_trip_success_rate
            FROM pipeline_statistics 
            ORDER BY processing_start_time DESC LIMIT 1
        """)
        latest_run = cursor.fetchone()
        if latest_run:
            stats['latest_run'] = dict(latest_run)
        
        return stats
    
    def analyze_round_trip_results(self) -> Dict[str, Any]:
        """Analyze round-trip testing results in detail."""
        analysis = {}
        
        # Overall round-trip statistics
        cursor = self.conn.execute("""
            SELECT 
                COUNT(*) as total_tests,
                SUM(CASE WHEN is_lossless THEN 1 ELSE 0 END) as lossless_tests,
                SUM(CASE WHEN exact_match THEN 1 ELSE 0 END) as exact_matches,
                SUM(CASE WHEN normalized_match THEN 1 ELSE 0 END) as normalized_matches,
                AVG(similarity_score) as avg_similarity,
                AVG(levenshtein_distance) as avg_levenshtein_distance
            FROM round_trip_tests
        """)
        row = cursor.fetchone()
        analysis['overall'] = dict(row)
        
        # Round-trip results by source scheme
        cursor = self.conn.execute("""
            SELECT 
                source_scheme,
                COUNT(*) as total_tests,
                SUM(CASE WHEN is_lossless THEN 1 ELSE 0 END) as lossless_tests,
                AVG(similarity_score) as avg_similarity
            FROM round_trip_tests
            GROUP BY source_scheme
            ORDER BY lossless_tests DESC
        """)
        analysis['by_source_scheme'] = [dict(row) for row in cursor.fetchall()]
        
        # Failed round-trip examples (first 10)
        cursor = self.conn.execute("""
            SELECT 
                rt.original_content,
                rt.converted_content, 
                rt.round_trip_content,
                rt.similarity_score,
                rt.levenshtein_distance
            FROM round_trip_tests rt
            WHERE NOT rt.is_lossless
            ORDER BY rt.similarity_score ASC
            LIMIT 10
        """)
        analysis['failed_examples'] = [dict(row) for row in cursor.fetchall()]
        
        return analysis
    
    def analyze_discovered_patterns(self) -> Dict[str, Any]:
        """Analyze discovered patterns from extensible mapping."""
        analysis = {}
        
        # Pattern counts by type
        cursor = self.conn.execute("""
            SELECT 
                pattern_type,
                COUNT(*) as unique_patterns,
                SUM(frequency_count) as total_occurrences,
                AVG(confidence_score) as avg_confidence
            FROM discovered_patterns
            GROUP BY pattern_type
            ORDER BY total_occurrences DESC
        """)
        analysis['by_type'] = [dict(row) for row in cursor.fetchall()]
        
        # Patterns by sakha-veda combination
        cursor = self.conn.execute("""
            SELECT 
                detected_in_sakha_veda,
                COUNT(*) as unique_patterns,
                SUM(frequency_count) as total_occurrences
            FROM discovered_patterns
            GROUP BY detected_in_sakha_veda
            ORDER BY total_occurrences DESC
        """)
        analysis['by_sakha_veda'] = [dict(row) for row in cursor.fetchall()]
        
        # Top 20 most frequent patterns
        cursor = self.conn.execute("""
            SELECT 
                source_pattern,
                target_mapping,
                pattern_type,
                frequency_count,
                confidence_score,
                detected_in_sakha_veda
            FROM discovered_patterns
            ORDER BY frequency_count DESC
            LIMIT 20
        """)
        analysis['most_frequent'] = [dict(row) for row in cursor.fetchall()]
        
        # Patterns with low confidence (potential false positives)
        cursor = self.conn.execute("""
            SELECT 
                source_pattern,
                target_mapping,
                pattern_type,
                confidence_score,
                frequency_count
            FROM discovered_patterns
            WHERE confidence_score < 0.7
            ORDER BY frequency_count DESC
            LIMIT 10
        """)
        analysis['low_confidence'] = [dict(row) for row in cursor.fetchall()]
        
        return analysis
    
    def analyze_quality_by_source(self) -> Dict[str, Any]:
        """Analyze quality metrics by different dimensions."""
        analysis = {}
        
        # Quality by source
        cursor = self.conn.execute("""
            SELECT 
                s.name as source_name,
                COUNT(t.id) as total_texts,
                AVG(t.quality_score) as avg_quality_score,
                SUM(CASE WHEN t.round_trip_valid THEN 1 ELSE 0 END) as successful_round_trips,
                AVG(t.discovered_patterns_count) as avg_patterns_per_text
            FROM texts t
            JOIN sources s ON t.source_id = s.id
            GROUP BY s.id, s.name
            ORDER BY avg_quality_score DESC
        """)
        analysis['by_source'] = [dict(row) for row in cursor.fetchall()]
        
        # Quality by sakha-veda combination
        cursor = self.conn.execute("""
            SELECT 
                v.name as veda,
                sk.name as sakha,
                COUNT(t.id) as total_texts,
                AVG(t.quality_score) as avg_quality_score,
                SUM(CASE WHEN t.round_trip_valid THEN 1 ELSE 0 END) as successful_round_trips
            FROM texts t
            JOIN sakhas sk ON t.sakha_id = sk.id
            JOIN vedas v ON sk.veda_id = v.id
            GROUP BY v.id, sk.id
            ORDER BY avg_quality_score DESC
        """)
        analysis['by_sakha_veda'] = [dict(row) for row in cursor.fetchall()]
        
        # Quality by extension scheme
        cursor = self.conn.execute("""
            SELECT 
                extension_scheme_used,
                COUNT(*) as texts_processed,
                AVG(quality_score) as avg_quality_score,
                SUM(CASE WHEN round_trip_valid THEN 1 ELSE 0 END) as successful_round_trips
            FROM texts
            WHERE extension_scheme_used IS NOT NULL
            GROUP BY extension_scheme_used
            ORDER BY avg_quality_score DESC
        """)
        analysis['by_extension_scheme'] = [dict(row) for row in cursor.fetchall()]
        
        return analysis
    
    def analyze_source_detection(self) -> Dict[str, Any]:
        """Analyze source detection accuracy and performance."""
        analysis = {}
        
        # Detection confidence distribution
        cursor = self.conn.execute("""
            SELECT 
                detected_scheme,
                COUNT(*) as file_count,
                AVG(confidence_score) as avg_confidence,
                MIN(confidence_score) as min_confidence,
                MAX(confidence_score) as max_confidence
            FROM source_detections
            GROUP BY detected_scheme
            ORDER BY file_count DESC
        """)
        analysis['by_detected_scheme'] = [dict(row) for row in cursor.fetchall()]
        
        # Low confidence detections (potential misclassifications)
        cursor = self.conn.execute("""
            SELECT 
                file_path,
                detected_scheme,
                confidence_score,
                matched_rule
            FROM source_detections
            WHERE confidence_score < 0.8
            ORDER BY confidence_score ASC
            LIMIT 10
        """)
        analysis['low_confidence_detections'] = [dict(row) for row in cursor.fetchall()]
        
        # Detection by features
        cursor = self.conn.execute("""
            SELECT 
                has_pua_codes,
                COUNT(*) as file_count,
                AVG(confidence_score) as avg_confidence
            FROM source_detections
            GROUP BY has_pua_codes
        """)
        analysis['by_pua_presence'] = [dict(row) for row in cursor.fetchall()]
        
        return analysis
    
    def generate_visualizations(self, output_dir: Path):
        """Generate visualizations for the analysis."""
        plt.style.use('seaborn-v0_8')
        
        # 1. Round-trip success rate by source
        cursor = self.conn.execute("""
            SELECT 
                s.name as source_name,
                COUNT(tl.id) as total_lines,
                SUM(CASE WHEN tl.round_trip_valid THEN 1 ELSE 0 END) as successful_lines
            FROM text_lines tl
            JOIN texts t ON tl.text_id = t.id
            JOIN sources s ON t.source_id = s.id
            GROUP BY s.id, s.name
        """)
        
        source_data = cursor.fetchall()
        if source_data:
            sources = [row[0] for row in source_data]
            success_rates = [row[2] / row[1] if row[1] > 0 else 0 for row in source_data]
            
            plt.figure(figsize=(10, 6))
            bars = plt.bar(sources, success_rates)
            plt.title('Round-trip Success Rate by Source')
            plt.ylabel('Success Rate')
            plt.xlabel('Source')
            plt.xticks(rotation=45)
            
            # Add value labels on bars
            for bar, rate in zip(bars, success_rates):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                        f'{rate:.2%}', ha='center', va='bottom')
            
            plt.tight_layout()
            plt.savefig(output_dir / 'round_trip_success_by_source.png', dpi=300)
            plt.close()
        
        # 2. Pattern discovery by type
        cursor = self.conn.execute("""
            SELECT pattern_type, COUNT(*) as count
            FROM discovered_patterns
            GROUP BY pattern_type
            ORDER BY count DESC
        """)
        
        pattern_data = cursor.fetchall()
        if pattern_data:
            types = [row[0] for row in pattern_data]
            counts = [row[1] for row in pattern_data]
            
            plt.figure(figsize=(8, 8))
            plt.pie(counts, labels=types, autopct='%1.1f%%', startangle=90)
            plt.title('Discovered Patterns by Type')
            plt.axis('equal')
            plt.savefig(output_dir / 'patterns_by_type.png', dpi=300)
            plt.close()
        
        # 3. Quality score distribution
        cursor = self.conn.execute("SELECT quality_score FROM texts WHERE quality_score IS NOT NULL")
        quality_scores = [row[0] for row in cursor.fetchall()]
        
        if quality_scores:
            plt.figure(figsize=(10, 6))
            plt.hist(quality_scores, bins=20, alpha=0.7, edgecolor='black')
            plt.title('Distribution of Quality Scores')
            plt.xlabel('Quality Score')
            plt.ylabel('Frequency')
            plt.axvline(sum(quality_scores) / len(quality_scores), color='red', 
                       linestyle='--', label=f'Mean: {sum(quality_scores) / len(quality_scores):.3f}')
            plt.legend()
            plt.tight_layout()
            plt.savefig(output_dir / 'quality_score_distribution.png', dpi=300)
            plt.close()
    
    def generate_comprehensive_report(self, output_dir: Path):
        """Generate a comprehensive HTML report."""
        overall_stats = self.get_overall_statistics()
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Udapaana Pipeline Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; }}
                .metric {{ background-color: #e8f4f8; padding: 10px; margin: 5px 0; border-radius: 3px; }}
                .success {{ background-color: #d4edda; color: #155724; }}
                .warning {{ background-color: #fff3cd; color: #856404; }}
                .error {{ background-color: #f8d7da; color: #721c24; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Udapaana Enhanced Pipeline Analysis Report</h1>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="section">
                <h2>Overall Statistics</h2>
                <div class="metric">Total Texts Processed: {overall_stats.get('total_texts', 0):,}</div>
                <div class="metric">Total Lines Processed: {overall_stats.get('total_lines', 0):,}</div>
                <div class="metric">Total Patterns Discovered: {overall_stats.get('total_patterns', 0):,}</div>
                <div class="metric {'success' if overall_stats.get('round_trip_success_rate', 0) > 0.9 else 'warning' if overall_stats.get('round_trip_success_rate', 0) > 0.7 else 'error'}">
                    Round-trip Success Rate: {overall_stats.get('round_trip_success_rate', 0):.2%}
                </div>
                <div class="metric">Average Confidence Score: {(overall_stats.get('average_confidence') or 0):.3f}</div>
            </div>
            
            <div class="section">
                <h2>Key Findings</h2>
                <ul>
                    <li>The pipeline successfully processed {overall_stats.get('total_texts', 0)} texts with line-by-line validation</li>
                    <li>Round-trip testing achieved {overall_stats.get('round_trip_success_rate', 0):.1%} success rate</li>
                    <li>Pattern discovery identified {overall_stats.get('total_patterns', 0)} unique patterns across all sources</li>
                    <li>Runtime extensible mappings enabled processing of previously unknown accent encodings</li>
                </ul>
            </div>
            
            <div class="section">
                <h2>Data Quality Assessment</h2>
                <p>Based on round-trip validation and pattern discovery analysis:</p>
                <ul>
                    <li><strong>Excellent</strong> (>95% success): Sources with standardized encoding</li>
                    <li><strong>Good</strong> (85-95% success): Sources with minor encoding variations</li>
                    <li><strong>Acceptable</strong> (70-85% success): Sources requiring custom mappings</li>
                    <li><strong>Needs Review</strong> (<70% success): Sources with significant encoding issues</li>
                </ul>
            </div>
            
            <div class="section">
                <h2>Recommendations</h2>
                <ol>
                    <li>Review texts with failed round-trip validation for potential encoding issues</li>
                    <li>Examine low-confidence pattern discoveries for false positives</li>
                    <li>Consider manual review of texts with quality scores below 0.8</li>
                    <li>Update extension configurations based on discovered patterns</li>
                    <li>Implement additional validation for texts with custom mappings</li>
                </ol>
            </div>
            
            <div class="section">
                <h2>Next Steps</h2>
                <ul>
                    <li>Export validated data for downstream applications</li>
                    <li>Create specialized views for different use cases (recitation, research, etc.)</li>
                    <li>Implement continuous validation as new sources are added</li>
                    <li>Develop quality metrics dashboard for ongoing monitoring</li>
                </ul>
            </div>
        </body>
        </html>
        """
        
        with open(output_dir / 'comprehensive_report.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def save_json_report(self, data: Dict[str, Any], file_path: Path):
        """Save analysis data as JSON."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
    
    def export_failed_round_trips_for_review(self, output_file: Path = None):
        """Export failed round-trip cases for manual review."""
        if output_file is None:
            output_file = Path("failed_round_trips_review.csv")
        
        cursor = self.conn.execute("""
            SELECT 
                t.title,
                s.name as source,
                v.name as veda,
                sk.name as sakha,
                tl.line_number,
                tl.content_original,
                tl.content_slp1_extended,
                tl.content_round_trip,
                tl.confidence_score,
                rt.similarity_score,
                rt.levenshtein_distance
            FROM text_lines tl
            JOIN texts t ON tl.text_id = t.id
            JOIN sources s ON t.source_id = s.id
            JOIN sakhas sk ON t.sakha_id = sk.id
            JOIN vedas v ON sk.veda_id = v.id
            LEFT JOIN round_trip_tests rt ON rt.text_line_id = tl.id
            WHERE NOT tl.round_trip_valid
            ORDER BY tl.confidence_score ASC, rt.similarity_score ASC
        """)
        
        df = pd.DataFrame(cursor.fetchall(), columns=[
            'title', 'source', 'veda', 'sakha', 'line_number',
            'original', 'converted', 'round_trip', 'confidence',
            'similarity', 'levenshtein_distance'
        ])
        
        df.to_csv(output_file, index=False, encoding='utf-8')
        logger.info(f"Exported {len(df)} failed round-trip cases to {output_file}")

if __name__ == "__main__":
    analyzer = UdapaanaPipelineAnalyzer()
    analyzer.analyze_all()
    analyzer.export_failed_round_trips_for_review()