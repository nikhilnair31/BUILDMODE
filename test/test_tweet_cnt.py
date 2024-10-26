import os
import time
import asyncio
from pathlib import Path
from twikit import Client
from dotenv import load_dotenv

load_dotenv()

USER_SCREEN_NAME = os.getenv('USER_SCREEN_NAME')
USERNAME = os.getenv('USERNAME')
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')

async def main():
    client = Client('en-US')
    await client.login(
        auth_info_1 = USERNAME,
        auth_info_2 = EMAIL,
        password = PASSWORD
    )
    
    user = await client.get_user_by_screen_name(USER_SCREEN_NAME)
    print(
        f'\n###########################################\n',
        f'id: {user.id}',
        f'name: {user.name}',
        f'followers: {user.followers_count}',
        f'tweets count: {user.statuses_count}',
        f'\n###########################################\n',
        sep='\n'
    )

    started_time = time.time()

    cursor_file = Path("cursor.txt")
    cursor = None
    if cursor_file.exists():
        cursor = cursor_file.read_text()

    # Get all posts
    cursor_cnt = 0
    all_tweets = []
    tweets = await user.get_tweets('Tweets')
    cursor_cnt += 1
    all_tweets += tweets
    print(f'Cursor cnt: {cursor_cnt}, Length of tweets: {len(all_tweets)}')
    
    cursor = tweets.next_cursor
    cursor_file.write_text(cursor)

    while len(all_tweets) < 50:
        tweets = await tweets.next()
        cursor_cnt += 1
        all_tweets += tweets
        cursor_file.write_text(tweets.next_cursor)
        print(f'Cursor cnt: {cursor_cnt}, Length of tweets: {len(all_tweets)}')

    print(
        f'Time: {time.time() - started_time}'
    )

asyncio.run(main())