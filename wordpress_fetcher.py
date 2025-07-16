#!/usr/bin/env python3
"""
WordPress Data Fetcher - Main script to fetch and process WordPress data.
"""
import os
import base64
import argparse
from dotenv import load_dotenv
import nltk

# Make sure nltk data is downloaded
nltk.download('punkt')

# Import functions from local modules
from api import list_public_post_types
from dataframe import build_wordpress_analytics_dataframe, save_dataframe_to_csv

# Help function definitions
def print_api_help():
    """Print help information for API functions."""
    print("\n=== WordPress API Functions Help ===\n")
    print("Functions for interacting with the WordPress REST API\n")
    print("fetch_wordpress_analytics(url, header)")
    print("  Fetches analytics data for a specific URL from WordPress\n")
    print("fetch_posts_by_date_range(start_date, end_date, header, per_page=100)")
    print("  Fetches all post URLs within a specified date range\n")
    print("list_public_post_types()")
    print("  Lists all public post types available via the WordPress REST API\n")
    print("Example:")
    print("  from api import list_public_post_types")
    print("  list_public_post_types()")

def print_content_help():
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

def print_util_help():
    """Print help information for utility functions."""
    print("\n=== Utility Functions Help ===\n")
    print("Utility functions for URL processing and other tasks\n")
    print("create_url_regex_pattern(url)")
    print("  Creates a regex pattern for matching URLs in analytics platforms\n")
    print("Example:")
    print("  from util import create_url_regex_pattern")
    print("  pattern = create_url_regex_pattern('https://www.yourwebsite.com/2023/01/post-name/')")

def print_dataframe_help():
    """Print help information for dataframe functions."""
    print("\n=== DataFrame Functions Help ===\n")
    print("Functions for building and managing DataFrames from WordPress data\n")
    print("build_wordpress_analytics_dataframe(start_date, end_date, header)")
    print("  Builds a complete DataFrame with analytics data for posts in date range\n")
    print("save_dataframe_to_csv(df, start_date, end_date)")
    print("  Saves a DataFrame to CSV with proper handling of complex data types\n")
    print("Example:")
    print("  from dataframe import build_wordpress_analytics_dataframe, save_dataframe_to_csv")
    print("  df = build_wordpress_analytics_dataframe('2023-01-01', '2023-02-01', header)")
    print("  save_dataframe_to_csv(df, '2023-01-01', '2023-02-01')")
def main():
    """Main function to fetch and process data from the WordPress API."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Fetch WordPress analytics data for a date range.")
    parser.add_argument('--start_date', required=False, help='Start date in YYYY-MM-DD format')
    parser.add_argument('--end_date', required=False, help='End date in YYYY-MM-DD format')
    parser.add_argument('--list-types', action='store_true', help='List available post types and exit')
    parser.add_argument('--help-api', action='store_true', help='Show help for API functions')
    parser.add_argument('--help-content', action='store_true', help='Show help for content processing functions')
    parser.add_argument('--help-util', action='store_true', help='Show help for utility functions')
    parser.add_argument('--help-dataframe', action='store_true', help='Show help for dataframe functions')
    args = parser.parse_args()

    # Load environment variables from .env file
    load_dotenv()
    
    # Get credentials securely from environment variables
    wordpress_user = os.environ.get('WORDPRESS_USER')
    wordpress_password = os.environ.get('WORDPRESS_PASSWORD')
    
    # Check for help flags
    if args.help_api:
        print_api_help()
        return
        
    if args.help_content:
        print_content_help()
        return
        
    if args.help_util:
        print_util_help()
        return
        
    if args.help_dataframe:
        print_dataframe_help()
        return
    
    # Check if both dates are provided when needed
    if not args.list_types and (not args.start_date or not args.end_date):
        parser.error("--start_date and --end_date are required unless --list-types is specified")
    
    # Check if credentials are available
    if not wordpress_user or not wordpress_password:
        raise ValueError("WordPress credentials not found in environment variables")
    
    # Define the header for the request
    wordpress_credentials = wordpress_user + ":" + wordpress_password
    wordpress_token = base64.b64encode(wordpress_credentials.encode())
    wordpress_header = {'Authorization': 'Basic ' + wordpress_token.decode('utf-8')}
    
    # If --list-types flag is set, list available post types and exit
    if args.list_types:
        list_public_post_types()
        return
    
    # Use dates from arguments
    start_date = args.start_date
    end_date = args.end_date
    
    # Build DataFrame
    df = build_wordpress_analytics_dataframe(start_date, end_date, wordpress_header)
    
    # Save to CSV
    save_dataframe_to_csv(df, start_date, end_date)
    
    return df

if __name__ == "__main__":
    main()

# Example usage:
# python3 wordpress_fetcher.py --start_date 2024-07-01 --end_date 2025-06-30
# python3 wordpress_fetcher.py --list-types
# python3 wordpress_fetcher.py --help-api
# python3 wordpress_fetcher.py --help-content
# python3 wordpress_fetcher.py --help-util
# python3 wordpress_fetcher.py --help-dataframe