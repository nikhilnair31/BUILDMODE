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

    tweets = await user.get_tweets('Tweets')
    for tweet in tweets:
        print(f'tweet: {tweet}')

asyncio.run(main())