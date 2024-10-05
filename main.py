import json
import logging
from flask import Flask, render_template, request, jsonify
import markdown
import requests
from datetime import datetime

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
    logging.info(f"Fetching latest release for {repo}")
    release = get_latest_release(repo)
    if release:
        logging.info(f"Successfully fetched latest release for {repo}")
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
        logging.warning(f"Failed to fetch latest release for {repo}")
        return None

def get_repos_from_request():
    """
    Get the list of repositories from the request JSON data.

    Returns:
        list: A list of repository names.
    """
    data = request.get_json()
    return data.get('repos', [])

def update_cache(repos):
    """
    Update the cache with the latest release notes for all watched repositories.
    """
    logging.info("Starting cache update")
    logging.info(f"Received {len(repos)} repositories")
    
    release_notes = []
    failed_repos = []
    for repo in repos:
        try:
            logging.info(f"Fetching release notes for {repo}")
            notes = extract_release_notes(repo)
            if notes:
                release_notes.append(notes)
                logging.info(f"Successfully fetched release notes for {repo}")
            else:
                logging.warning(f"No release notes found for {repo}")
                failed_repos.append(repo)
        except Exception as e:
            logging.error(f"Error fetching release notes for {repo}: {str(e)}")
            failed_repos.append(repo)
    
    logging.info(f"Fetched release notes for {len(release_notes)} out of {len(repos)} repositories")
    if failed_repos:
        logging.warning(f"Failed to fetch release notes for: {', '.join(failed_repos)}")
    
    release_notes.sort(key=lambda x: x['published_at'], reverse=True)
    
    cache_data = {
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'release_notes': release_notes,
        'failed_repos': failed_repos
    }
    
    logging.info("Cache update completed")
    return cache_data

def read_cache(cache_data):
    """
    Process the cached release notes.
    """
    release_notes = cache_data.get('release_notes', [])
    
    # Recalculate age_in_days based on the current date
    for note in release_notes:
        published_date = datetime.strptime(note['published_at'], '%Y-%m-%dT%H:%M:%SZ')
        note['age_in_days'] = (datetime.utcnow() - published_date).days
    
    return release_notes, cache_data.get('last_updated', 'Unknown')

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
    """
    cache_data = request.args.get('cache', '{}')
    cache_data = json.loads(cache_data)
    release_notes, last_updated = read_cache(cache_data)
    
    display_last_updated = calculate_age_in_days(last_updated)
    
    return render_template('index.html', release_notes=release_notes, last_updated=display_last_updated)

@app.route('/update', methods=['POST'])
def update():
    """
    Update the cache and return the new cache data.
    """
    logging.info("Update request received")
    repos = get_repos_from_request()
    new_cache_data = update_cache(repos)
    logging.info("Update completed")
    return jsonify(new_cache_data)

@app.route('/settings')
def settings():
    """
    Render the settings page.

    Returns:
        str: The rendered HTML of the settings page.
    """
    return render_template('settings.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0')
