#!/usr/bin/env python3
"""
Pre-commit hook for detecting PII using Microsoft Presidio.

This script scans staged files in a git commit for personally identifiable
information (PII) and alerts the user if any is found.
"""

import sys
import subprocess
from collections import defaultdict
from typing import Dict, List, Tuple

try:
    from presidio_analyzer import AnalyzerEngine
    from presidio_analyzer.nlp_engine import NlpEngineProvider
except ImportError:
    print("Error: presidio-analyzer is not installed.")
    print("Please install it with: pip install -r requirements.txt")
    sys.exit(1)


def get_staged_files() -> List[str]:
    """Get list of staged files from git."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
            check=True
        )
        files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
        return files
    except subprocess.CalledProcessError as e:
        print(f"Error getting staged files: {e}")
        return []


def get_file_content(filepath: str) -> str:
    """Get the staged content of a file."""
    try:
        result = subprocess.run(
            ["git", "show", f":{filepath}"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError:
        # If git show fails, try reading the file directly
        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()
        except Exception:
            return ""


def analyze_text_for_pii(text: str, analyzer: AnalyzerEngine) -> List[Dict]:
    """Analyze text for PII using Presidio."""
    results = analyzer.analyze(
        text=text,
        language='en',
        entities=None,  # Analyze all entity types
        return_decision_process=False
    )
    return results


def get_line_number(text: str, char_position: int) -> Tuple[int, int]:
    """Get line number and column from character position."""
    lines = text[:char_position].split('\n')
    line_number = len(lines)
    column = len(lines[-1]) + 1 if lines else 1
    return line_number, column


def format_pii_findings(
    filepath: str, 
    content: str, 
    results: List
) -> Tuple[Dict[str, int], List[str]]:
    """Format PII findings for display."""
    pii_counts = defaultdict(int)
    details = []
    
    for result in results:
        entity_type = result.entity_type
        pii_counts[entity_type] += 1
        
        # Get the actual PII text
        pii_text = content[result.start:result.end]
        
        # Get line number
        line_num, col = get_line_number(content, result.start)
        
        # Get context (the line containing the PII)
        lines = content.split('\n')
        # line_num is 1-based, lines array is 0-based
        if 0 < line_num <= len(lines):
            context_line = lines[line_num - 1]
        else:
            # Edge case: if line calculation is off, use the PII text itself
            context_line = pii_text
        
        detail = (
            f"  {filepath}:{line_num}:{col} - {entity_type} "
            f"(score: {result.score:.2f})\n"
            f"    Found: '{pii_text}'\n"
            f"    Context: {context_line.strip()}"
        )
        details.append(detail)
    
    return dict(pii_counts), details


def should_skip_file(filepath: str) -> bool:
    """Determine if a file should be skipped from PII analysis."""
    skip_extensions = {
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico',
        '.pdf', '.zip', '.tar', '.gz', '.exe', '.dll', '.so',
        '.pyc', '.class', '.jar', '.war'
    }
    
    skip_patterns = {
        '.git/', 'node_modules/', '__pycache__/', '.venv/',
        'venv/', 'build/', 'dist/', '.eggs/'
    }
    
    # Check extension
    for ext in skip_extensions:
        if filepath.lower().endswith(ext):
            return True
    
    # Check patterns
    for pattern in skip_patterns:
        if pattern in filepath:
            return True
    
    return False


def main():
    """Main function to run PII detection on staged files."""
    print("🔍 Running PII detection on staged files...")
    
    # Initialize Presidio analyzer
    try:
        # Create NLP engine with spaCy
        configuration = {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
        }
        provider = NlpEngineProvider(nlp_configuration=configuration)
        nlp_engine = provider.create_engine()
        analyzer = AnalyzerEngine(nlp_engine=nlp_engine)
    except Exception as e:
        print(f"Error initializing Presidio: {e}")
        print("Please ensure spaCy model is installed: python -m spacy download en_core_web_sm")
        sys.exit(1)
    
    # Get staged files
    staged_files = get_staged_files()
    
    if not staged_files:
        print("No staged files to analyze.")
        return 0
    
    print(f"Analyzing {len(staged_files)} file(s)...\n")
    
    # Analyze each file
    total_pii_counts = defaultdict(int)
    all_details = []
    files_with_pii = []
    
    for filepath in staged_files:
        if should_skip_file(filepath):
            continue
        
        content = get_file_content(filepath)
        if not content:
            continue
        
        # Analyze for PII
        results = analyze_text_for_pii(content, analyzer)
        
        if results:
            files_with_pii.append(filepath)
            pii_counts, details = format_pii_findings(filepath, content, results)
            
            # Update totals
            for entity_type, count in pii_counts.items():
                total_pii_counts[entity_type] += count
            
            all_details.extend(details)
    
    # Report results
    if total_pii_counts:
        print("⚠️  WARNING: PII detected in your commit!\n")
        
        print("📊 PII Summary:")
        print("-" * 60)
        for entity_type, count in sorted(total_pii_counts.items()):
            print(f"  {entity_type}: {count}")
        print("-" * 60)
        print(f"  Total PII instances: {sum(total_pii_counts.values())}")
        print(f"  Files affected: {len(files_with_pii)}\n")
        
        print("📍 PII Locations:")
        print("-" * 60)
        for detail in all_details:
            print(detail)
            print()
        
        print("-" * 60)
        print("\n⛔ Commit blocked due to PII detection.")
        print("Please review and remove PII before committing.")
        print("If this is intentional, you can bypass with: git commit --no-verify\n")
        
        return 1
    else:
        print("✅ No PII detected. Commit allowed.\n")
        return 0


if __name__ == "__main__":
    sys.exit(main())
