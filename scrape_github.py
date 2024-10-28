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
    calculate_time_spent_per_language,
    summarize_projects
)

def scrape_github_func(con, cur):
    # Initialize database tables
    database_create_github_user(cur)
    database_create_github_repo(cur)

    # Fetch GitHub user and repository data
    username = get_user_details()
    print(f"GitHub Username is {username}\n")

    full_repo_data = get_repo_details()
    print(f"Fetched {len(full_repo_data)} GitHub repos' data!\n")

    language_count = Counter()
    total_time_per_lang = Counter()
    technologies = set()
    repo_explainers = []
    
    # Process each repository
    for repo_data in full_repo_data:
        # print(f"repo_data: {repo_data}\n")

        _, _, repo_created_at, repo_updated_at, repo_languages_json, repo_tech, _, _, repo_explain_txt, _ = repo_data
        database_insert_github_repo(con, cur, repo_data)
        
        repo_explainers.append(repo_explain_txt)

        repo_tech = repo_tech.split(' | ')
        technologies.update(repo_tech)

        repo_languages = json.loads(repo_languages_json)
        language_count.update(repo_languages)

        for lang, time in calculate_time_spent_per_language(repo_created_at, repo_updated_at, repo_languages).items():
            total_time_per_lang[lang] += time

    language_percentage = calculate_language_percentage(language_count)
    print(f"Language Usage Percentage: {language_percentage}\n")

    technologies_used = ' | '.join(list(technologies))
    print(f"Technologies Used: {technologies_used}\n")

    sorted_total_time_per_lang = dict(sorted(total_time_per_lang.items(), key=lambda item: item[1], reverse=True))
    sorted_total_time_per_lang_json = json.dumps(sorted_total_time_per_lang)
    print(f"Total Time Spent per Language: {sorted_total_time_per_lang_json}\n")

    print(f"Repo Explainers Fetched: {len(repo_explainers)}\n")
    total_summary = ""
    repo_explainers_txt = ' | '.join(repo_explainers)
    project_summaries = summarize_projects(repo_explainers_txt)
    for summary in project_summaries:
        total_summary += f'- {summary}\n'
    print(f"Project Summaries:\n{total_summary}\n")

    user_data = (username, language_percentage, sorted_total_time_per_lang_json, technologies_used, repo_explainers_txt, total_summary)
    database_insert_github_user(con, cur, user_data)
    print("Inserted GitHub user data!\n")

    print(f'Scraped all GitHub repos!\n')