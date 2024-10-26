from db import (
    database_create_github
)
from gith import (
    get_repo_details,
    calculate_language_percentage,
    summarize_projects
)

def scrape_github_func(con, cur):
    # database_create_github(cur)

    print("Fetching GitHub user data...\n")

    repo_data = get_repo_details()
    print(f"Number of Repositories: {len(repo_data)}\n")

    language_percentage = calculate_language_percentage(repo_data['language_count'])
    print(f"Language Usage Percentage: {language_percentage}\n")

    technologies_used = list(repo_data['technologies'])
    print(f"Technologies Used: {technologies_used}\n")

    print(f"Repo Explainers Fetched: {len(repo_data['repo_explainers'])}\n")
    project_summaries = summarize_projects(repo_data['repo_explainers'])
    print("Project Summaries:")
    for summary in project_summaries:
        print(f" - {summary}")
    print(f"\n")