import os
import requests
from dotenv import load_dotenv
from collections import defaultdict, Counter
from api import (
    openai_init, 
    openai_chat
)

load_dotenv()

GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')
GITHUB_ACCESS_TOKEN = os.getenv('GITHUB_ACCESS_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

headers = {'Authorization': f'token {GITHUB_ACCESS_TOKEN}'}
base_url = f'https://api.github.com/users/{GITHUB_USERNAME}'

# Function to make a GitHub API request
def make_github_request(url):
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

# 1. Fetch Repos and Analyze
def get_repo_details():
    repos = make_github_request(f'{base_url}/repos')
    # print(f'repos\n{repos}\n')

    language_count = Counter()
    technologies = set()
    repo_explainers = []

    for repo in repos:
        print(f'-----------------------------------')
        print(f'repo: {repo}')

        repo_id = repo['id']
        print(f'repo_id: {repo_id}')

        repo_name = repo['name']
        print(f'repo_name: {repo_name}')
        
        repo_created_at = repo['created_at']
        print(f'repo_created_at: {repo_created_at}')
        
        repo_updated_at = repo['updated_at']
        print(f'repo_updated_at: {repo_updated_at}')
        
        languages_url = repo['languages_url']
        languages = make_github_request(languages_url)
        print(f'languages: {languages}')
        language_count.update(languages)

        technologies.update(languages.keys())
        print(f'technologies: {languages.keys()}')
        
        repo_description = repo.get('description', '')
        print(f'repo_description: {repo_description}')

        commits_url = f'https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/commits'
        commits = make_github_request(commits_url)
        commit_cnt = len(commits)
        print(f'commit_cnt: {commit_cnt}')
        
        readme_url = f'https://raw.githubusercontent.com/{GITHUB_USERNAME}/{repo_name}/refs/heads/master/README.md'
        print(f'readme_url: {readme_url}')
        try:
            readme_response = requests.get(readme_url)
            if readme_response.status_code == 200:
                print(f'Got README!')
                repo_explainers.append(f'{repo_name} - {readme_response.text}')
            else:
                repo_explainers.append(f'{repo_name} - {repo_description}')
                print(f"Error fetching README :(")
        except Exception as e:
            print(f"Error fetching README: {e}")

    return {
        "language_count": language_count,
        "technologies": technologies,
        "repo_explainers": repo_explainers,
    }

# 3. Calculate Language Percentage
def calculate_language_percentage(language_count):
    total = sum(language_count.values())
    
    # Calculate percentage and round to 1 decimal place, then sort by percentage
    language_percentage = {
        lang: round((count / total) * 100, 1) for lang, count in language_count.items()
    }
    
    # Sort the dictionary by percentage in descending order
    sorted_perc = dict(sorted(language_percentage.items(), key=lambda item: item[1], reverse=True))

    return sorted_perc

# 4. Generate Project Summaries using OpenAI
def summarize_projects(descriptions):
    summaries = []

    for description in descriptions:
        if description:
            openai_client = openai_init(OPENAI_API_KEY)
            response = openai_chat(
                client = openai_client, 
                model = "gpt-4o-mini",
                messages = [
                    {
                        "role": "system",
                        "content": f"Summarize the provided project descriptions"
                    },
                    {
                        "role": "user",
                        "content": f"{description}"
                    }
                ]
            )
            summaries.append(response)
    
    return summaries