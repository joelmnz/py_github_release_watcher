import json
from flask import Flask, render_template, request, redirect, url_for
import markdown
import requests
from datetime import datetime
import os
import argparse

app = Flask(__name__)

# Set up argument parsing
parser = argparse.ArgumentParser(description='Release Notes Cache Directory')
parser.add_argument('--cache-dir', type=str, required=True, help='Directory to store cache files')
args = parser.parse_args()

# Use the provided cache directory to set CACHE_FILE
CACHE_FILE = os.path.join(args.cache_dir, 'release_notes_cache.json')

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
            return cache_data.get('release_notes', []), cache_data.get('last_updated', 'Unknown')
    return [], 'Unknown'

@app.route('/')
def index():
    """
    Render the index page with the cached release notes.

    Returns:
        str: The rendered HTML of the index page.
    """
    release_notes, last_updated = read_cache()
    return render_template('index.html', release_notes=release_notes, last_updated=last_updated)

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
    app.run()
