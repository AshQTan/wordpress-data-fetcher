"""
DataFrame creation and manipulation functions for WordPress data.
"""
import pandas as pd
import time
import csv

from api import fetch_posts_by_date_range, fetch_wordpress_analytics
from content import clean_html_content, analyze_reading_level
from util import create_url_regex_pattern

def build_wordpress_analytics_dataframe(start_date, end_date, header):
    """
    Fetch posts between the given dates and build a DataFrame with selected analytics data.
    
    Args:
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        header (dict): Authorization header for WordPress API
        
    Returns:
        pandas.DataFrame: DataFrame containing WordPress analytics data with clean content and reading level
    """
    # Get all post URLs within the date range
    post_urls = fetch_posts_by_date_range(start_date, end_date, header)
    
    # Save post_urls to a CSV for tracking
    post_urls_filename = f"wordpress_URLs_{start_date}_to_{end_date}.csv"
    pd.DataFrame({'url': post_urls}).to_csv(post_urls_filename, index=False, encoding='utf-8')
    print(f"Saved {len(post_urls)} post URLs to {post_urls_filename}")

    # Initialize empty lists for each column
    data = {
        'url': [],
        'regex': [],  # New column for regex pattern
        'date_published': [],
        'title': [],
        'content': [],
        'label': [],
        'topics': [],
        'primary_topic': [],
        'research_teams': [],
        'word_count': [],
        'reading_level': []  # New column for reading grade level
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
            
            # Extract primary topic name
            primary_topic = post_data.get('primary_topic', {})
            data['primary_topic'].append(primary_topic.get('name', '') if primary_topic else '')
            
            # Extract research team names
            research_teams = post_data.get('research_teams', [])
            research_team_names = [team.get('name', '') for team in research_teams] if research_teams else []
            data['research_teams'].append(research_team_names)
            
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
            data['primary_topic'].append('')
            data['research_teams'].append([])
            data['word_count'].append(0)
            data['reading_level'].append(None)  # Add None for reading level on error
    
    # Create DataFrame
    df = pd.DataFrame(data)
    print(f"DataFrame built with {len(df)} rows")
    
    return df

def save_dataframe_to_csv(df, start_date, end_date):
    """
    Save the DataFrame to a CSV file, with proper handling of complex data types.
    
    Args:
        df (pandas.DataFrame): DataFrame to save
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        
    Returns:
        str: Name of the output file
    """
    output_filename = f"wordpress_analytics_{start_date}_to_{end_date}.csv"
    
    # Remove 'content' column before saving to CSV to avoid issues with commas
    if 'content' in df.columns:
        df_to_save = df.drop(columns=['content'])
    else:
        df_to_save = df.copy()
    
    # Flatten list columns for CSV compatibility
    list_columns = ['topics', 'research_teams']
    for col in list_columns:
        if col in df_to_save.columns:
            df_to_save[col] = df_to_save[col].apply(lambda x: ';'.join(x) if isinstance(x, list) else x)
            
    # Save with robust quoting and UTF-8 encoding
    df_to_save.to_csv(output_filename, index=False, encoding='utf-8', quoting=csv.QUOTE_ALL)
    print(f"Data saved to {output_filename}")
    
    return output_filename
