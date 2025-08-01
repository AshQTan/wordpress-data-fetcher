#!/usr/bin/env python3
"""
WordPress API functions for fetching content from a WordPress site.
"""
import time
import requests
import argparse

def fetch_wordpress_analytics(url, header):
    """
    Fetch the response from querying the WP API with a specific url.
    
    Args:
        url (str): The URL to query for analytics data
        header (dict): Authorization header for WordPress API
        
    Returns:
        dict: JSON response from the WordPress API
    """
    queryurl = 'https://www.yourwebsite.com/wp-json/site-api/v3/analytics/query-by-url/'
    
    try:
        response = requests.post(queryurl, json={'url': url}, headers=header)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed for {url}: {str(e)}")
        return {}

def fetch_posts_by_date_range(start_date, end_date, header, per_page=100):
    """
    Fetch all post URLs from WordPress within a given date range.
    
    Args:
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        header (dict): Authorization header for WordPress API
        per_page (int): Number of posts to fetch per request (max 100)
        
    Returns:
        list: List of post URLs within the specified date range
    """
    # Format dates for the WordPress API (requires ISO 8601 format)
    start_date_iso = f"{start_date}T00:00:00Z"
    end_date_iso = f"{end_date}T23:59:59Z"
    
    # List of publication post types to fetch
    pub_types = ['post-type-1', 'post-type-2', 'post-type-3', 'post-type-4', 'post-type-5']
    # Map to endpoint names (usually the same as the post type slug)
    endpoint_map = {
        'post-type-1': 'post-type-1',
        'post-type-2': 'post-type-2',
        'post-type-3': 'post-type-3',
        'post-type-4': 'post-type-4',
        'post-type-5': 'post-type-5',
    }

    def fetch_urls_from_endpoint(endpoint):
        urls = []
        page = 1
        total_pages = 1
        while page <= total_pages:
            params = {
                'after': start_date_iso,
                'before': end_date_iso,
                'per_page': per_page,
                'page': page,
                '_fields': 'id,date,link'
            }
            response = requests.get(endpoint, params=params, headers=header)
            if response.status_code == 200:
                posts = response.json()
                for post in posts:
                    urls.append(post['link'])
                if page == 1:
                    total_pages = int(response.headers.get('X-WP-TotalPages', 1))
                    total_posts = int(response.headers.get('X-WP-Total', 0))
                    print(f"Found {total_posts} posts across {total_pages} pages at {endpoint}")
                print(f"Processed page {page}/{total_pages} - {len(posts)} posts from {endpoint}")
                page += 1
            else:
                print(f"Error fetching posts from {endpoint}: {response.status_code}")
                print(response.text)
                break
            time.sleep(0.5)
        return urls

    print(f"Fetching publications of types: {', '.join(pub_types)} between {start_date} and {end_date}...")
    all_urls = []
    for pub_type in pub_types:
        endpoint = f"https://www.yourwebsite.com/wp-json/wp/v2/{endpoint_map[pub_type]}"
        urls = fetch_urls_from_endpoint(endpoint)
        all_urls.extend(urls)
    print(f"Finished fetching {len(all_urls)} post URLs (all publication types)")
    return all_urls

def list_public_post_types():
    """
    List all public post types available via the WordPress REST API for your site.
    
    Returns:
        list: List of public post types available via REST API
    """
    api_url = "https://www.yourwebsite.com/wp-json/wp/v2/"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        endpoints = response.json()
        post_types = []
        for key in endpoints.keys():
            # Only include endpoints that look like post types (not taxonomies, etc.)
            if key not in ["types", "statuses", "taxonomies", "users", "media", "comments", "settings"]:
                post_types.append(key)
        print("Public post types available via REST API:")
        for pt in post_types:
            print(f"- {pt}")
        return post_types
    except Exception as e:
        print(f"Error fetching post types: {e}")
        return []

def print_help():
    """Print help information for API functions."""
    print("\n=== WordPress API Functions Help ===\n")
    print("Functions for interacting with the WordPress REST API\n")
    print("fetch_wordpress_analytics(url, header)")
    print("  Fetches analytics data for a specific URL from WordPress\n")
    print("fetch_posts_by_date_range(start_date, end_date, header, per_page=100)")
    print("  Fetches all post URLs within a specified date range\n")
    print("list_public_post_types()")
    print("  Lists all public post types available via the WordPress REST API\n")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WordPress API Functions")
    parser.add_argument('--help', action='store_true', help='Show detailed help for this module')
    parser.add_argument('--list-types', action='store_true', help='List available post types')
    args = parser.parse_args()
    
    if args.help:
        print_help()
    elif args.list_types:
        list_public_post_types()
    else:
        print_help()
