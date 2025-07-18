#!/usr/bin/env python3
"""
WordPress Topic Fetcher - Fetch WordPress posts that match specific topic tags within a date range.
"""
import os
import base64
import argparse
import requests
import pandas as pd
import time
import csv
from dotenv import load_dotenv

# Import relevant functions from our existing modules
from api import fetch_wordpress_analytics
from content import clean_html_content, analyze_reading_level
from util import create_url_regex_pattern
from dataframe import save_dataframe_to_csv

def fetch_posts_by_topics(start_date, end_date, topics, header, per_page=100):
    """
    Fetch all post URLs from WordPress that match specified topics within a given date range.
    
    Args:
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        topics (list): List of topic tags to filter by
        header (dict): Authorization header for WordPress API
        per_page (int): Number of posts to fetch per request (max 100)
        
    Returns:
        list: List of post URLs matching the specified topics within the date range
    """
    # Format dates for the WordPress API (requires ISO 8601 format)
    start_date_iso = f"{start_date}T00:00:00Z"
    end_date_iso = f"{end_date}T23:59:59Z"
    
    # List of publication post types to fetch
    pub_types = ['post-type-1', 'post-type-2', 'post-type-3', 'post-type-4', 'post-type-5']
    # Map to endpoint names
    endpoint_map = {
        'post-type-1': 'post-type-1',
        'post-type-2': 'post-type-2',
        'post-type-3': 'post-type-3',
        'post-type-4': 'post-type-4',
        'post-type-5': 'post-type-5',
    }
    
    # Convert topics list to comma-separated string for API parameters
    topic_param = ','.join(topics) if isinstance(topics, list) else topics
    
    def fetch_urls_from_endpoint(endpoint):
        urls = []
        matching_posts = []
        page = 1
        total_pages = 1
        
        while page <= total_pages:
            params = {
                'after': start_date_iso,
                'before': end_date_iso,
                'per_page': per_page,
                'page': page,
                'topics': topic_param,  # Filter by topics
                '_fields': 'id,date,link,title,topics'  # Include topics for verification
            }
            
            response = requests.get(endpoint, params=params, headers=header)
            if response.status_code == 200:
                posts = response.json()
                for post in posts:
                    # Verify if the post actually contains any of the requested topics
                    if 'topics' in post:
                        post_topics = [topic.get('name', '').lower() for topic in post.get('topics', [])]
                        if any(t.lower() in post_topics for t in topics):
                            urls.append(post['link'])
                            matching_posts.append({
                                'id': post.get('id', ''),
                                'title': post.get('title', {}).get('rendered', ''),
                                'link': post['link'],
                                'date': post.get('date', '')
                            })
                
                if page == 1:
                    total_pages = int(response.headers.get('X-WP-TotalPages', 1))
                    total_posts = int(response.headers.get('X-WP-Total', 0))
                    print(f"Found {total_posts} posts across {total_pages} pages at {endpoint}")
                
                print(f"Processed page {page}/{total_pages} - Found {len(posts)} posts from {endpoint}")
                page += 1
            else:
                print(f"Error fetching posts from {endpoint}: {response.status_code}")
                print(response.text)
                break
            
            time.sleep(0.5)
        
        return urls, matching_posts

    print(f"Fetching publications of types: {', '.join(pub_types)} between {start_date} and {end_date} with topics: {topic_param}")
    all_urls = []
    all_matching_posts = []
    
    for pub_type in pub_types:
        endpoint = f"https://www.yourwebsite.com/wp-json/wp/v2/{endpoint_map[pub_type]}"
        urls, matching_posts = fetch_urls_from_endpoint(endpoint)
        all_urls.extend(urls)
        all_matching_posts.extend(matching_posts)
    
    print(f"Finished fetching {len(all_urls)} post URLs matching topics: {topic_param}")
    return all_urls, all_matching_posts

def build_topic_analytics_dataframe(start_date, end_date, topics, header):
    """
    Fetch posts with specified topics between the given dates and build a DataFrame with analytics data.
    
    Args:
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        topics (list): List of topic tags to filter by
        header (dict): Authorization header for WordPress API
        
    Returns:
        pandas.DataFrame: DataFrame containing WordPress analytics data with clean content and reading level
    """
    # Get all post URLs matching the topics within the date range
    post_urls, matching_posts = fetch_posts_by_topics(start_date, end_date, topics, header)
    
    # Save matching_posts to a CSV for reference
    matching_posts_filename = f"wordpress_topic_matches_{start_date}_to_{end_date}.csv"
    pd.DataFrame(matching_posts).to_csv(matching_posts_filename, index=False, encoding='utf-8')
    print(f"Saved {len(matching_posts)} matching posts metadata to {matching_posts_filename}")
    
    # Save post_urls to a CSV for tracking
    post_urls_filename = f"wordpress_topic_URLs_{start_date}_to_{end_date}.csv"
    pd.DataFrame({'url': post_urls}).to_csv(post_urls_filename, index=False, encoding='utf-8')
    print(f"Saved {len(post_urls)} post URLs to {post_urls_filename}")

    # Initialize empty lists for each column
    data = {
        'url': [],
        'regex': [],
        'date_published': [],
        'title': [],
        'content': [],
        'label': [],
        'topics': [],
        'word_count': [],
        'reading_level': []
    }

    # Progress tracking
    total_posts = len(post_urls)
    print(f"Building DataFrame for {total_posts} posts...")
    
    # Process each URL
    for i, url in enumerate(post_urls):
        try:
            # Get analytics data for the URL
            post_data = fetch_wordpress_analytics(url, header)
            
            # Extract the required fields
            print(f"Processing ({i+1}/{total_posts}): {url}...")
            data['url'].append(url)
            # Add regex pattern for this url
            data['regex'].append(create_url_regex_pattern(url))
            
            # Get date_published and strip time portion
            date_published = post_data.get('date_published', '')
            date_only = date_published.split(' ')[0] if date_published else ''
            data['date_published'].append(date_only)
            
            data['title'].append(post_data.get('title', ''))
            
            # Clean content before adding to dataframe
            raw_content = post_data.get('content', '')
            cleaned_content = clean_html_content(raw_content)
            data['content'].append(cleaned_content)
            
            # Calculate reading level for the cleaned content
            reading_level = analyze_reading_level(cleaned_content)
            data['reading_level'].append(reading_level)
            
            # Extract label name if it exists
            label = post_data.get('label', {})
            data['label'].append(label.get('name', '') if label else '')
            
            # Extract topic names
            topics = post_data.get('topics', [])
            topic_names = [topic.get('name', '') for topic in topics] if topics else []
            data['topics'].append(topic_names)
            
            # Extract word count
            data['word_count'].append(post_data.get('word_count', 0))
            
            # Print progress
            if (i + 1) % 10 == 0 or (i + 1) == total_posts:
                print(f"Processed {i + 1}/{total_posts} posts")
                
            # Add a small delay to avoid overloading the API
            time.sleep(0.2)
            
        except Exception as e:
            print(f"Error processing URL {url}: {str(e)}")
            # Add empty values for this failed URL
            data['url'].append(url)
            data['regex'].append('')
            data['date_published'].append('')
            data['title'].append('')
            data['content'].append('')
            data['label'].append('')
            data['topics'].append([])
            data['word_count'].append(0)
            data['reading_level'].append(None)  # Add None for reading level on error
    
    # Create DataFrame
    df = pd.DataFrame(data)
    print(f"DataFrame built with {len(df)} rows")
    
    return df

def print_help():
    """Print help information for the WordPress Topic Fetcher."""
    print("\n=== WordPress Topic Fetcher Help ===\n")
    print("This script fetches WordPress posts that match specific topic tags within a date range.\n")
    print("Command Line Arguments:")
    print("  --start-date DATE    Start date in YYYY-MM-DD format")
    print("  --end-date DATE      End date in YYYY-MM-DD format")
    print("  --topics TOPICS      Comma-separated list of topic tags to filter by")
    print("  --list-topics        List all available topics in your WordPress site")
    print("  --help               Show this help message\n")
    print("Example:")
    print("  python wordpress_topic_fetcher.py --start-date 2023-01-01 --end-date 2023-12-31 --topics technology,science")

def list_available_topics(header):
    """
    List all available topics/tags in the WordPress site.
    
    Args:
        header (dict): Authorization header for WordPress API
    """
    try:
        # Most WordPress sites use 'tags' or 'categories' as taxonomy endpoints
        endpoints = [
            'https://www.yourwebsite.com/wp-json/wp/v2/topics', 
            'https://www.yourwebsite.com/wp-json/wp/v2/tags',
            'https://www.yourwebsite.com/wp-json/wp/v2/categories'
        ]
        
        topics_found = False
        
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, headers=header, params={'per_page': 100})
                if response.status_code == 200:
                    topics = response.json()
                    print(f"\nFound {len(topics)} topics at {endpoint}:\n")
                    
                    # Sort topics by name
                    topics.sort(key=lambda x: x.get('name', '').lower())
                    
                    for topic in topics:
                        print(f"- {topic.get('name', '')} (ID: {topic.get('id', '')})")
                    
                    topics_found = True
                    
                    # Check if there are more pages
                    total_pages = int(response.headers.get('X-WP-TotalPages', 1))
                    if total_pages > 1:
                        print(f"\nShowing page 1 of {total_pages}. To see more topics, use pagination.")
            except Exception as e:
                print(f"Error trying endpoint {endpoint}: {str(e)}")
        
        if not topics_found:
            print("\nNo topics found. Your WordPress site may use a different taxonomy structure.")
            print("Check your WordPress REST API documentation for the correct taxonomy endpoints.")
    
    except Exception as e:
        print(f"Error listing topics: {str(e)}")

def main():
    """Main function to fetch and process WordPress posts by topic."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Fetch WordPress posts by topic within a date range.")
    parser.add_argument('--start-date', help='Start date in YYYY-MM-DD format')
    parser.add_argument('--end-date', help='End date in YYYY-MM-DD format')
    parser.add_argument('--topics', help='Comma-separated list of topic tags to filter by')
    parser.add_argument('--list-topics', action='store_true', help='List all available topics in your WordPress site')
    parser.add_argument('--help', action='store_true', help='Show detailed help for this script')
    args = parser.parse_args()
    
    # Show help and exit if requested
    if args.help:
        print_help()
        return
    
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
    
    # If --list-topics flag is set, list available topics and exit
    if args.list_topics:
        list_available_topics(wordpress_header)
        return
    
    # Check if required parameters are provided
    if not args.start_date or not args.end_date or not args.topics:
        parser.error("--start-date, --end-date, and --topics are required unless --list-topics or --help is specified")
    
    # Parse topics into a list
    topic_list = [topic.strip() for topic in args.topics.split(',')]
    
    # Use dates from arguments
    start_date = args.start_date
    end_date = args.end_date
    
    # Build DataFrame
    df = build_topic_analytics_dataframe(start_date, end_date, topic_list, wordpress_header)
    
    # Save to CSV
    output_file = save_dataframe_to_csv(df, start_date, end_date)
    print(f"\nFinal output saved to: {output_file}")
    
    return df

if __name__ == "__main__":
    main()

# Example usage:
# python wordpress_topic_fetcher.py --start-date 2023-01-01 --end-date 2023-12-31 --topics technology,science
# python wordpress_topic_fetcher.py --list-topics
# python wordpress_topic_fetcher.py --help
