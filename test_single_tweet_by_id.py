import os
import time
import json
import asyncio
from pathlib import Path
from twikit import Client
from dotenv import load_dotenv
from helper import serialize_clean

load_dotenv()

USER_SCREEN_NAME = os.getenv('USER_SCREEN_NAME')
USERNAME = os.getenv('USERNAME')
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')

async def pull_single_tweet_by_id():
    client = Client('en-US')
    await client.login(
        auth_info_1 = USERNAME,
        auth_info_2 = EMAIL,
        password = PASSWORD
    )

    TWEET_ID = '1847835596569350340'
    tweet = await client.get_tweet_by_id(TWEET_ID)
    print(
        f'{tweet}',
        sep='\n'
    )

    tweet_json = serialize_clean(tweet)
    print(
        f'{tweet_json}',
        sep='\n'
    )

asyncio.run(pull_single_tweet_by_id())