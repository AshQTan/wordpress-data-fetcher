# WordPress Data Fetcher

This project provides modular tools for fetching and analyzing WordPress content through the WordPress REST API.

> **Note:** Replace `yourwebsite.com` with your actual website domain in all examples and code.

## Modules

The project has been organized into the following modules:

- `wordpress_fetcher/api.py`: Functions for interacting with the WordPress REST API
- `wordpress_fetcher/content.py`: Tools for cleaning HTML content and analyzing reading level
- `wordpress_fetcher/util.py`: Utility functions like URL pattern generation for analytics
- `wordpress_fetcher/dataframe.py`: Data processing and manipulation functions
- `wordpress_fetcher.py`: Main script for fetching WordPress data by date range

## Prerequisites

- Python 3.6+
- WordPress site with REST API enabled
- User credentials with appropriate permissions

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Environment Setup

Create a `.env` file in the project directory with your WordPress credentials:

```
WORDPRESS_USER=your_username
WORDPRESS_PASSWORD=your_password
```

## Input Format

No input files are required. The script fetches data directly from the WordPress API based on date parameters.

## Usage

### Fetching Content by Date Range

The main script allows you to fetch WordPress content published within a specific date range:

```bash
python wordpress_fetcher.py --start_date 2024-01-01 --end_date 2024-03-31
```

### Listing Available Post Types

To see all available post types from your WordPress site:

```bash
python wordpress_fetcher.py --list-types
```

## Output Files

The script generates two files:

1. `wordpress_URLs_<start_date>_to_<end_date>.csv`: Contains just the URLs fetched
2. `wordpress_analytics_<start_date>_to_<end_date>.csv`: Contains detailed analytics for each URL

### Output Data Structure

The analytics CSV contains the following columns:

- `url`: The full URL of the post
- `regex`: A regex pattern for matching the URL in Google Analytics
- `date_published`: The publication date (YYYY-MM-DD)
- `title`: The post title
- `label`: The content label (if applicable)
- `topics`: List of topics (semicolon-separated)
- `primary_topic`: The primary topic (if applicable)
- `research_teams`: List of research teams (semicolon-separated)
- `word_count`: Number of words in the content
- `reading_level`: Flesch-Kincaid grade level score

Note: The `content` column is excluded from CSV output to avoid formatting issues with commas.

## Module Usage

If you want to incorporate these functions in your own scripts, you can import the modules directly:

### Fetching Posts by Date Range

```python
from wordpress_fetcher.api import fetch_posts_by_date_range
import base64
import os

# Create authentication header
wordpress_user = os.environ.get('WORDPRESS_USER')
wordpress_password = os.environ.get('WORDPRESS_PASSWORD')
wordpress_credentials = wordpress_user + ":" + wordpress_password
wordpress_token = base64.b64encode(wordpress_credentials.encode())
header = {'Authorization': 'Basic ' + wordpress_token.decode('utf-8')}

# Fetch URLs
urls = fetch_posts_by_date_range('2024-01-01', '2024-01-31', header)
print(f"Found {len(urls)} URLs")
```

### Cleaning HTML Content

```python
from wordpress_fetcher.content import clean_html_content

html = "<p>This is <strong>formatted</strong> content with <a href='#'>links</a>.</p>"
clean_text = clean_html_content(html)
print(clean_text)
```

### Analyzing Reading Level

```python
from wordpress_fetcher.content import analyze_reading_level

text = "This is a sample text to analyze for readability."
grade_level = analyze_reading_level(text)
print(f"Reading grade level: {grade_level}")
```

### Creating a URL Regex Pattern for Analytics

```python
from wordpress_fetcher.util import create_url_regex_pattern

url = "https://www.yourwebsite.com/2024/02/15/sample-article/"
pattern = create_url_regex_pattern(url)
print(f"Regex pattern: {pattern}")
```

### Building a Complete Analytics DataFrame

```python
from wordpress_fetcher.dataframe import build_wordpress_analytics_dataframe, save_dataframe_to_csv

# Create authentication header as shown above

# Build DataFrame
df = build_wordpress_analytics_dataframe('2024-01-01', '2024-01-31', header)

# Save to CSV
output_file = save_dataframe_to_csv(df, '2024-01-01', '2024-01-31')
print(f"Data saved to {output_file}")
```

## Customizing for Your WordPress Site

### Modifying Post Types

Edit the `pub_types` and `endpoint_map` variables in `wordpress_fetcher/api.py` to match the post types available on your WordPress site:

```python
pub_types = ['posts', 'fact-sheet', 'decoded', 'short-read', 'quiz']
endpoint_map = {
    'posts': 'posts',
    'fact-sheet': 'fact-sheet',
    'decoded': 'decoded',
    'short-read': 'short-read',
    'quiz': 'quiz',
}
```

To see all available post types on your site, run:

```bash
python wordpress_fetcher.py --list-types
```

### Changing API Endpoints

If your WordPress site uses different API endpoints, modify the URLs in `wordpress_fetcher/api.py`:

```python
queryurl = 'https://www.yourwebsite.com/wp-json/prc-api/v3/analytics/query-by-url/'
```

## WordPress REST API Authentication

This script uses Basic Authentication for simplicity, but for production environments, consider using more secure authentication methods like OAuth.

### Basic Authentication Setup

1. Store your credentials in a `.env` file (never commit this file to version control)
2. The script loads these credentials and creates an authentication header
3. This header is passed to all API requests

For improved security:

1. Create a dedicated API user with limited permissions
2. Use HTTPS for all API requests
3. Consider implementing a token-based authentication system

## Troubleshooting

### API Connection Issues

If you encounter connection errors:

1. Verify your WordPress credentials
2. Check that your WordPress site has REST API enabled
3. Ensure your user has appropriate permissions
4. Check network connectivity to your WordPress site

### Missing Data

If the output CSV is missing expected data:

1. Check that your WordPress site has the expected post types
2. Verify that content was published within the specified date range
3. Ensure your user has access to view all required content
4. Check for API rate limiting issues

### Performance Issues

If the script runs slowly:

1. Reduce the date range to process fewer posts
2. Adjust the sleep time in API requests (currently 0.2-0.5 seconds)
3. Consider using pagination to process posts in smaller batches

## References

- [WordPress REST API Handbook](https://developer.wordpress.org/rest-api/)
- [Python Pandas Documentation](https://pandas.pydata.org/docs/)
- [Readability Metrics Documentation](https://pypi.org/project/readability-metrics/)
