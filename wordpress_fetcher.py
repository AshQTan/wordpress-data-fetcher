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
def main():
    """Main function to fetch and process data from the WordPress API."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Fetch WordPress analytics data for a date range.")
    parser.add_argument('--start_date', required=True, help='Start date in YYYY-MM-DD format')
    parser.add_argument('--end_date', required=True, help='End date in YYYY-MM-DD format')
    parser.add_argument('--list-types', action='store_true', help='List available post types and exit')
    args = parser.parse_args()

    # Load environment variables from .env file
    load_dotenv()
    
    # Get credentials securely from environment variables
    wordpress_user = os.environ.get('WORDPRESS_USER')
    wordpress_password = os.environ.get('WORDPRESS_PASSWORD')
    
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