import os
import time
from twikit import Client
from dotenv import load_dotenv

load_dotenv()

USER_SCREEN_NAME = os.getenv('USER_SCREEN_NAME')
USERNAME = os.getenv('USERNAME')
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
TOTAL_TWEETS = os.getenv('TOTAL_TWEETS')
RATE_LIMIT = os.getenv('RATE_LIMIT')
RESET_INTERVAL = os.getenv('RESET_INTERVAL')

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
        media_url_httpss = [media_item["media_url_https"] for media_item in tweet.media] if tweet.media else "-"
        media_url_httpss_str = ' | '.join(media_url_httpss)
        print(
            f'id: {tweet.id}',
            f'full_text: {full_text}',
            f'created_at_datetime: {created_at_datetime}',
            f'media_url_httpss_str: {media_url_httpss_str}',
            sep='\n'
        )

        cleaned_tweets.append(
            (tweet_id,created_at_datetime,full_text,media_url_httpss_str)
        )
    
    return cleaned_tweets

# Get user tweets
async def get_user_tweets(con, cur, user):
    tweets = []
    user_tweets = await user.get_tweets('Tweets', count='10')
    tweets.extend(user_tweets)
    
    while len(tweets) < TOTAL_TWEETS:
        # Check if we've hit the rate limit
        if len(tweets) % RATE_LIMIT == 0 and len(tweets) > 0:
            print(f"Reached rate limit. Waiting for {RESET_INTERVAL} seconds.")
            time.sleep(RESET_INTERVAL)
        
        while user_tweets := await user_tweets.next():
            if not user_tweets or len(tweets) >= TOTAL_TWEETS:
                break
            tweets.extend(user_tweets)
    
    cleaned_tweets = clean_tweets(tweets)

    return cleaned_tweets