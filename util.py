"""
Utility functions for WordPress data processing.
"""
import re

def create_url_regex_pattern(url):
    """
    Process a URL to create a regex pattern for matching in GA4.
    Escapes only regex metacharacters, not slashes or hyphens.
    
    Args:
        url (str): The URL to process
        
    Returns:
        str: A regex pattern for matching the URL in GA4 pagePath dimension
    """
    if url.startswith("https://www.yourwebsite.com/"):
        processed_url = url.replace("https://www.yourwebsite.com/", "", 1)
    else:
        processed_url = url
        
    # Check for URLs with pattern containing /YYYY/MM/DD/
    date_pattern = r'/(\d{4}/\d{1,2}/\d{1,2}/.*)'
    match = re.search(date_pattern, processed_url)
    if match:
        # Keep only the date pattern and what follows
        processed_url = match.group(1)
    else:
        processed_url = processed_url    
        
    processed_url = processed_url[:80]
    print(processed_url)
    
    # Only escape regex metacharacters, not slashes or hyphens
    regex_metachars = r'.^$*+?{}[]\\|()'
    escaped_url = ''.join(['\\' + c if c in regex_metachars else c for c in processed_url])
    regex_pattern = f"{escaped_url}"
    
    return regex_pattern
