import json
from flask import Flask, render_template, request, redirect, url_for
import markdown
import requests
from datetime import datetime, timedelta

import os

app = Flask(__name__)

# Read the cache directory from an environment variable
CACHE_DIR = os.environ.get('CACHE_DIR', '.')
CACHE_FILE = os.path.join(CACHE_DIR, 'release_notes_cache.json')

def get_latest_release(repo):
    """
    Fetch the latest release information for a given GitHub repository.

    Args:
        repo (str): The repository in the format 'owner/repo'.

    Returns:
        dict: A dictionary containing the release information if successful, None otherwise.
    """
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def extract_release_notes(repo):
    """
    Extract release notes from the latest release of a given GitHub repository.

    Args:
        repo (str): The repository in the format 'owner/repo'.

    Returns:
        dict: A dictionary containing the release notes, version, and other metadata if successful, None otherwise.
    """
    release = get_latest_release(repo)
    if release:
        version = release['tag_name']
        body = release['body']
        published_at = release['published_at']
        body_html = markdown.markdown(body)
        published_date = datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%SZ')
        age_in_days = (datetime.utcnow() - published_date).days
        return {
            'repo': repo,
            'version': version,
            'body': body_html,
            'published_at': published_at,
            'age_in_days': age_in_days,
        }
    else:
        return None

def read_repos_from_file(filename):
    """
    Read a list of repositories from a file.

    Args:
        filename (str): The path to the file containing the list of repositories.

    Returns:
        list: A list of repository names.
    """
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line.strip() and not line.strip().startswith('#')]

def update_cache():
    """
    Update the cache with the latest release notes for all watched repositories.
    """
    repos = read_repos_from_file('watched_repos.txt')
    release_notes = []
    for repo in repos:
        notes = extract_release_notes(repo)
        if notes:
            release_notes.append(notes)
    
    release_notes.sort(key=lambda x: x['published_at'], reverse=True)
    
    cache_data = {
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'release_notes': release_notes
    }
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache_data, f)
    except IOError as e:
        print(f"Error writing to cache file: {e}")

def read_cache():
    """
    Read the cached release notes from the cache file.

    Returns:
        tuple: A tuple containing a list of release notes and the last updated timestamp.
    """
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            cache_data = json.load(f)
            release_notes = cache_data.get('release_notes', [])
            
            # Recalculate age_in_days based on the current date
            for note in release_notes:
                published_date = datetime.strptime(note['published_at'], '%Y-%m-%dT%H:%M:%SZ')
                note['age_in_days'] = (datetime.utcnow() - published_date).days
                #note['age_in_days'] = calculate_age_in_days(published_date)
            
            return release_notes, cache_data.get('last_updated', 'Unknown')
    return [], 'Unknown'

def calculate_age_in_days(date_string):
    """
    Calculate how old a given date is and return a formatted string.

    Args:
        date_string (str): The date string in the format 'YYYY-MM-DD HH:MM:SS'.

    Returns:
        str: Formatted string indicating the date and how many days ago it was.
    """
    # Parse the date string into a datetime object
    date_dt = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
    
    # Get the current time
    now = datetime.now()
    
    # Calculate the difference
    time_difference = now - date_dt
    
    # Format the date
    formatted_date = date_dt.strftime('%Y-%m-%d %I:%M %p')
    
    # Determine how many days ago it was updated
    days_ago = time_difference.days
    if days_ago == 0:
        time_ago = "today"
    elif days_ago == 1:
        time_ago = "1 day ago"
    else:
        time_ago = f"{days_ago} days ago"
    
    # Combine the formatted date with the time ago
    return f"{formatted_date} ({time_ago})"

@app.route('/')
def index():
    """
    Render the index page with the cached release notes.

    Returns:
        str: The rendered HTML of the index page.
    """
    release_notes, last_updated = read_cache()
    
    # Use the calculate_age_in_days function to format the last_updated
    display_last_updated = calculate_age_in_days(last_updated)
    
    return render_template('index.html', release_notes=release_notes, last_updated=display_last_updated)

@app.route('/update', methods=['POST'])
def update():
    """
    Update the cache and redirect to the index page.

    Returns:
        werkzeug.wrappers.Response: A redirect response to the index page.
    """
    update_cache()
    return redirect(url_for('index'))

if __name__ == "__main__":
    if not os.path.exists(CACHE_FILE):
        update_cache()
    app.run(host='0.0.0.0')