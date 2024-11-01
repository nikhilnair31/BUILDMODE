import os
import time
import json
import asyncio
from pathlib import Path
from twikit import Client
from dotenv import load_dotenv
import sys
from pathlib import Path

# Add parent directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from helper import serialize_clean

load_dotenv()

USER_SCREEN_NAME = os.getenv('USER_SCREEN_NAME')
USERNAME = os.getenv('USERNAME')
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')

async def pull_multiple_tweets():
    client = Client('en-US')
    await client.login(
        auth_info_1 = USERNAME,
        auth_info_2 = EMAIL,
        password = PASSWORD
    )
    
    user = await client.get_user_by_screen_name(USER_SCREEN_NAME)

    tweets = await user.get_tweets('Tweets')
    for idx, tweet in enumerate(tweets):
        tweet_json = serialize_clean(tweet)
        print(
            f'{idx}: {tweet_json["text"]}',
            sep='\n'
        )

asyncio.run(pull_multiple_tweets())