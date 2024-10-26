import json
from collections import defaultdict, Counter
from db import (
    database_create_github_user,
    database_create_github_repo,
    database_insert_github_user,
    database_insert_github_repo
)
from gith import (
    get_user_details,
    get_repo_details,
    calculate_language_percentage,
    summarize_projects
)

def scrape_github_func(con, cur):
    database_create_github_user(cur)
    database_create_github_repo(cur)

    username = get_user_details()
    print(f"GitHub Username is {username}\n")

    full_repo_data = get_repo_details()
    number_of_repos = len(full_repo_data)
    print(f"Fetched {number_of_repos} GitHub repos' data!\n")

    language_count = Counter()
    technologies = set()
    repo_explainers = []
    
    for repo_data in full_repo_data:
        # print(f"repo_data: {repo_data}\n")

        _, _, _, _, repo_languages_json, repo_tech, _, _, repo_explain_txt, _ = repo_data
        database_insert_github_repo(con, cur, repo_data)

        repo_tech = repo_tech.split(' | ')
        repo_languages = json.loads(repo_languages_json)

        language_count.update(repo_languages)
        technologies.update(repo_tech)
        repo_explainers.append(repo_explain_txt)

    language_percentage = calculate_language_percentage(language_count)
    print(f"Language Usage Percentage: {language_percentage}\n")

    technologies_used = ' | '.join(list(technologies))
    print(f"Technologies Used: {technologies_used}\n")

    print(f"Repo Explainers Fetched: {len(repo_explainers)}\n")
    total_summary = "-"
    repo_explainers_txt = ' | '.join(repo_explainers)
    project_summaries = summarize_projects(repo_explainers_txt)
    for summary in project_summaries:
        total_summary += f'- {summary}\n'
    print(f"Project Summaries:\n{total_summary}\n")

    user_data = (username, language_percentage, technologies_used, repo_explainers_txt, total_summary)
    database_insert_github_user(con, cur, user_data)
    print("Inserted GitHub user data!\n")