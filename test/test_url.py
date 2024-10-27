import re
from urllib.parse import quote_plus
from db import database_init, database_select_tweet_w_id

con, cur = database_init()

text = f'''
    I'll analyze more patterns from your social media activity and GitHub projects to suggest 3 more innovative ideas:

1. AI-Powered Game Level Curator
Inspired by posts: 1833923607678124093, 1831819479908823372, 1812322445191467339

A platform that:

Analyzes game level designs and provides insights on flow, difficulty, and engagement
Suggests improvements based on successful level patterns
Includes a community feature for sharing and rating level designs
Uses AI to generate level layouts based on successful patterns
Market Potential: Level design tools are crucial for both indie and professional game developers, with growing demand for AI-assisted design tools.

Challenges:

Creating accurate analysis algorithms
Handling different game genres
Ensuring generated suggestions are practical
2. Developer Workflow Assistant
Inspired by posts: 1835000228979651037, 1827668685319719691, 1816092188859580694

A tool that combines:

Smart code snippet management
AI-powered documentation generation
Project organization templates
Integration with popular IDEs and Cursor
Automated workflow suggestions based on coding patterns
Market Potential: Developer productivity tools are in high demand, especially those that integrate AI capabilities.

Challenges:

Creating seamless IDE integrations
Building an intuitive UX for developers
Maintaining security with code-related features
3. Real-time Game Analytics Visualizer
Inspired by posts: 1829515703638224952, 1810149568861900859, 1840593270696443991

A platform for indie game developers that:

Provides real-time player behavior analytics
Visualizes heat maps of player activity
Identifies potential game balance issues
Suggests optimizations based on player patterns
Integrates with Steam and other platforms
Market Potential: Growing indie game market needs accessible analytics tools that are typically only available to larger studios.

Challenges:

Processing large amounts of real-time data
Creating meaningful visualizations
Building platform integrations
These ideas align well with your technical background in C# and game development, plus your experience with AWS Lambda and AI integration shown in your GitHub repositories. Would you like me to elaborate on any of these concepts?
'''
pattern = r"\b\d{19}\b"
matches = re.findall(pattern, text)

for match in matches:
    print(f'-----------------------------------------------')
    print(f'match: {match}')
    post_data = database_select_tweet_w_id(cur, match)
    print(f'post_data: {post_data}')
    post_url, post_text = post_data

    if post_url != "-":
        post_urls = post_url.split(" | ")
        for post_url in post_urls:
            print(f'post_url: {post_url}')
    else:
        formatted_post_text = quote_plus(post_text)
        google_search_url = f'https://www.google.com/search?q=site:x.com+{formatted_post_text}'
        print(f'google_search_url: {google_search_url}')