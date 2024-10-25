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

async def pull_multiple_tweets():
    client = Client('en-US')
    await client.login(
        auth_info_1 = USERNAME,
        auth_info_2 = EMAIL,
        password = PASSWORD
    )
    
    user = await client.get_user_by_screen_name(USER_SCREEN_NAME)

    tweets = await user.get_tweets('Tweets')
    tweets_result = tweets.__dict__["_Result__results"]
    print(
        f'{tweets_result}',
        sep='\n'
    )
    
    tweets_data = [tweet.__dict__ for tweet in tweets_result]
    print(
        f'{tweets_data}',
        sep='\n'
    )
    
    tweets_json = json.dumps(tweets_data)
    print(
        f'{tweets_json}',
        sep='\n'
    )
    
    for tweet in tweets[:2]:
        print(f'--------------------\n{tweet.__dict__}\n--------------------\n')

asyncio.run(pull_multiple_tweets())