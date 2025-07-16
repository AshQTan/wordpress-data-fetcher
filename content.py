#!/usr/bin/env python3
"""
Content processing functions for WordPress content.
"""
import re
import html
import argparse
from readability import Readability as PyReadability

def clean_html_content(html_content):
    """
    Clean HTML content by removing tags, WordPress blocks, and formatting,
    returning plain text.
    
    Args:
        html_content (str): HTML content with WordPress blocks and formatting
        
    Returns:
        str: Clean text with HTML and formatting removed
    """
    if not html_content:
        return ""
    
    # Step 1: Remove WordPress block comments
    html_content = re.sub(r'<!--\s*/?wp:[^>]*-->', '', html_content)
    
    # Step 2: Remove HTML figure/image elements completely
    html_content = re.sub(r'<figure[^>]*>.*?</figure>', '', html_content, flags=re.DOTALL)
    
    # Step 3: Remove div containers
    html_content = re.sub(r'<div[^>]*>', '', html_content)
    html_content = re.sub(r'</div>', '', html_content)
    
    # Step 4: Remove heading tags but keep their content
    html_content = re.sub(r'<h[1-6][^>]*>', '', html_content)
    html_content = re.sub(r'</h[1-6]>', '\n\n', html_content)
    
    # Step 5: Handle list items - convert to text with bullets
    html_content = re.sub(r'<li[^>]*>', '• ', html_content)
    html_content = re.sub(r'</li>', '\n', html_content)
    
    # Step 6: Remove list containers
    html_content = re.sub(r'</?ul[^>]*>', '', html_content)
    html_content = re.sub(r'</?ol[^>]*>', '', html_content)
    
    # Step 7: Handle paragraphs - add newlines
    html_content = re.sub(r'<p[^>]*>', '', html_content)
    html_content = re.sub(r'</p>', '\n\n', html_content)
    
    # Step 8: Preserve link text but remove links
    links = re.findall(r'<a[^>]*>(.*?)</a>', html_content)
    for link in links:
        html_content = re.sub(r'<a[^>]*>.*?</a>', link, html_content, count=1)
    
    # Step 9: Remove any remaining HTML tags
    html_content = re.sub(r'<[^>]*>', '', html_content)
    
    # Step 10: Decode HTML entities
    html_content = html.unescape(html_content)
    
    # Step 11: Remove specific text artifacts
    html_content = re.sub(r'Summary\n', '', html_content)       
    html_content = html_content.replace('\xa0', ' ')           
    html_content = html_content.replace('\xad', '')            

    # Handle newlines separately - after other whitespace handling
    html_content = re.sub(r'\n{3,}', '\n\n', html_content)      
    html_content = re.sub(r' {2,}', ' ', html_content)          
    html_content = re.sub(r'^\s+', '', html_content, flags=re.MULTILINE)  
    html_content = re.sub(r'\s+$', '', html_content, flags=re.MULTILINE)  

    # Finally, replace newlines with periods (if desired)
    html_content = html_content.replace('\n', '. ')
    
    # Step 12: Remove other Unicode control and formatting characters
    html_content = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F-\x9F]', '', html_content)
    
    # Step 13: Fix whitespace issues
    html_content = re.sub(r'\n{3,}', '\n\n', html_content)      # Reduce multiple newlines
    html_content = re.sub(r' {2,}', ' ', html_content)          # Reduce multiple spaces
    html_content = re.sub(r'^\s+', '', html_content, flags=re.MULTILINE)  # Remove leading spaces
    html_content = re.sub(r'\s+$', '', html_content, flags=re.MULTILINE)  # Remove trailing spaces
    
    # Step 14: Clean up any specific patterns
    html_content = re.sub(r'\[/?collapsible\]', '', html_content)
    html_content = re.sub(r'_vscodedecoration_.*?\}', '', html_content)
    
    return html_content.strip()

def analyze_reading_level(text):
    """
    Analyze the reading level of text using Flesch-Kincaid grade level.
    
    Args:
        text (str): The text to analyze
        
    Returns:
        float: The Flesch-Kincaid grade level score (or None if analysis fails)
    """
    # Handle empty text
    if not text or len(text.strip()) == 0:
        print("Warning: Empty text provided for reading level analysis")
        return None
    
    try:
        # First ensure we have enough text for a meaningful analysis
        word_count = len(text.split())
        if word_count < 30:
            print(f"Warning: Text only has {word_count} words, which may be too few for reliable analysis")
        
        # Create a readability analyzer from the py-readability-metrics package
        r = PyReadability(text)
        
        # Get the Flesch-Kincaid grade level score
        grade_level = r.flesch_kincaid().grade_level
        
        return grade_level
        
    except Exception as e:
        print(f"Error analyzing reading level: {str(e)}")
        return None

def print_help():
    """Print help information for content processing functions."""
    print("\n=== Content Processing Functions Help ===\n")
    print("Tools for cleaning HTML content and analyzing reading level\n")
    print("clean_html_content(html_content)")
    print("  Removes HTML tags, WordPress blocks, and formatting from content\n")
    print("analyze_reading_level(text)")
    print("  Analyzes text and returns the Flesch-Kincaid grade level score\n")
    print("Example:")
    print("  from content import clean_html_content, analyze_reading_level")
    print("  clean_text = clean_html_content('<p>Some HTML content</p>')")
    print("  grade_level = analyze_reading_level(clean_text)")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Content Processing Functions for WordPress")
    parser.add_argument('--help', action='store_true', help='Show detailed help for this module')
    parser.add_argument('--clean', metavar='HTML', help='Clean HTML content and print the result')
    parser.add_argument('--analyze', metavar='TEXT', help='Analyze reading level of text')
    args = parser.parse_args()
    
    if args.help:
        print_help()
    elif args.clean:
        print(clean_html_content(args.clean))
    elif args.analyze:
        grade = analyze_reading_level(args.analyze)
        print(f"Reading grade level: {grade}")
    else:
        print_help()
