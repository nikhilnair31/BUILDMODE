import os
import re
import json
import time
from twikit import Client
from dotenv import load_dotenv

load_dotenv()

RATE_LIMIT = int(os.getenv('RATE_LIMIT'))
RESET_INTERVAL = int(os.getenv('RESET_INTERVAL'))
USER_SCREEN_NAME = os.getenv('USER_SCREEN_NAME')
USERNAME = os.getenv('USERNAME')
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')

# Initialize twitter client
async def tweet_login():
    client = Client(
        language = 'en-US',
    )
    await client.login(
        auth_info_1 = USERNAME,
        auth_info_2 = EMAIL,
        password = PASSWORD
    )

    return client

# Get user by screen name
async def tweet_user(client):
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
    
    return user

def clean_tweets(tweets):
    cleaned_tweets = []
    
    for tweet in tweets:
        tweet_id = tweet.id
        created_at_datetime = tweet.created_at_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
        full_text = tweet.full_text.strip()
        full_text_wo_rt = re.sub(r'RT @\w+:', '', full_text)
        full_text_wo_url = re.sub(r'http\S+', '', full_text_wo_rt)
        media = tweet.media
        media_str = json.dumps(media)
        media_url_httpss = [media_item["media_url_https"] for media_item in media] if media else "-"
        media_url_httpss_str = ' | '.join(media_url_httpss)
        print(
            f'id: {tweet.id}',
            f'full_text: {full_text_wo_url}',
            f'created_at_datetime: {created_at_datetime}',
            f'media_str: {media_str}',
            f'media_url_httpss_str: {media_url_httpss_str}',
            sep='\n'
        )

        cleaned_tweets.append(
            (tweet_id,created_at_datetime,full_text_wo_url,media_str,media_url_httpss_str)
        )
    
    return cleaned_tweets

# Get user tweets
async def get_user_tweets(con, cur, user):
    all_tweets = []

    cursor_file = Path("cursor.txt")
    cursor = None
    if cursor_file.exists():
        cursor = cursor_file.read_text()
    
    try:
        tweets = await user.get_tweets('Tweets')
        all_tweets += tweets
        print(f'Length of all tweets: {len(all_tweets)}')
    
        cursor = tweets.next_cursor
        cursor_file.write_text(cursor)
        
        # Check if we've hit the rate limit
        if len(all_tweets) % RATE_LIMIT == 0 and len(all_tweets) > 0:
            print(f"Reached rate limit. Waiting for {RESET_INTERVAL} seconds.")
            time.sleep(RESET_INTERVAL)
        
        while tweets := await tweets.next():
            if not tweets:
                break
            all_tweets += tweets
            print(f'Length of all tweets: {len(all_tweets)}')
            cursor_file.write_text(tweets.next_cursor)
    
    except Exception as e:
        print(f"Error: {e}")

    cleaned_tweets = clean_tweets(all_tweets)

    return cleaned_tweets