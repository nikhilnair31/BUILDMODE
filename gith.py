import os
import json
import requests
from dotenv import load_dotenv
from api import (
    openai_chat
)

load_dotenv()

# Function to make a GitHub API request
def make_github_request(url):
    GITHUB_ACCESS_TOKEN = os.getenv('GITHUB_ACCESS_TOKEN')

    if not GITHUB_ACCESS_TOKEN:
        st.error("Please add your GitHub Access Token to continue.")
        st.stop()

    headers = {'Authorization': f'token {GITHUB_ACCESS_TOKEN}'}

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    return response.json()

# Calculate Language Percentage
def calculate_language_percentage(language_count):
    # print(f"language_count.items(): {language_count.items()}")

    total = sum(language_count.values())
    
    # Calculate percentage and round to 1 decimal place, then sort by percentage
    language_percentage = {
        lang: round((count / total) * 100, 1) 
        for lang, count in language_count.items() 
        if lang not in ['Jupyter Notebook', 'ShaderLab', 'ASP', 'ASP.NET']
    }
    
    # Sort the dictionary by percentage in descending order
    sorted_perc = dict(sorted(language_percentage.items(), key=lambda item: item[1], reverse=True))

    return json.dumps(sorted_perc)

# Generate Project Summaries using OpenAI
def summarize_projects(descriptions_list_txt):
    summaries = []
    descriptions = descriptions_list_txt.split(' | ')
    for description in descriptions:
        if description:
            response = openai_chat(
                model = "gpt-4o-mini",
                messages = [
                    {
                        "role": "system",
                        "content": f"Summarize each GitHub repo's description/README into a single line explaining its purpose."
                    },
                    {
                        "role": "user",
                        "content": f"Descriptions\n{description}"
                    }
                ]
            )
            summaries.append(response)
    
    return summaries

# Fetch Repos and Analyze
def get_user_details():
    GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')

    if not GITHUB_USERNAME:
        st.error("Please add your GitHub Username to continue.")
        st.stop()

    return GITHUB_USERNAME

# Fetch Repos and Analyze
def get_repo_details():
    GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')

    if not GITHUB_USERNAME:
        st.error("Please add your GitHub Username to continue.")
        st.stop()

    base_url = f'https://api.github.com/users/{GITHUB_USERNAME}'
    repos = make_github_request(f'{base_url}/repos?per_page=1000')
    # print(f'repos\n{repos}\n')

    full_repo_data = []
    
    for repo in repos:
        # print(f'-----------------------------------')
        # print(f'repo: {repo}')

        repo_id = repo['id']

        repo_name = repo['name']
        
        repo_created_at = repo['created_at']
        
        repo_updated_at = repo['updated_at']
        
        languages_url = repo['languages_url']
        languages = make_github_request(languages_url)
        repo_languages_json = json.dumps(languages)

        tech = languages.keys()
        repo_tech = ' | '.join(list(tech))
        
        repo_description = repo.get('description', '')

        commits_url = f'https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/commits'
        commits = make_github_request(commits_url)
        repo_commit_cnt = len(commits)
        
        repo_explain_txt = '-'
        repo_readme_text = "-"
        readme_url = f'https://raw.githubusercontent.com/{GITHUB_USERNAME}/{repo_name}/refs/heads/master/README.md'
        try:
            readme_response = requests.get(readme_url)
            if readme_response.status_code == 200:
                repo_readme_text = readme_response.text
                repo_explain_txt = f'{repo_name} - {repo_readme_text}'
            else:
                repo_explain_txt = f'{repo_name} - {repo_description}'
        except Exception as e:
            print(f"Error fetching README: {e}")

        full_repo_data.append((
            repo_id, 
            repo_name, 
            repo_created_at, 
            repo_updated_at, 
            repo_languages_json, 
            repo_tech, 
            repo_description,
            repo_readme_text,
            repo_explain_txt,
            repo_commit_cnt,
        ))

    return full_repo_data