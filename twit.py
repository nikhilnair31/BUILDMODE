import os
import re
import json
import time
from twikit import Client
from dotenv import load_dotenv
from helper import serialize_clean

load_dotenv()

RATE_LIMIT = int(os.getenv('RATE_LIMIT'))
RESET_INTERVAL = int(os.getenv('RESET_INTERVAL'))
USER_SCREEN_NAME = os.getenv('USER_SCREEN_NAME')
USERNAME = os.getenv('USERNAME')
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')

# Converting the Tweet object to a JSON string
def format_tweet_dump_data(tweet_dump):
    tweets_result = tweet_dump.__dict__["_Result__results"]
    tweets_data = [serialize_clean(tweet) for tweet in tweets_result]
    tweets_json = json.dumps(tweets_data)

    return tweets_json
# Selecting relevant data
def clean_tweet_dump_data(tweets_str):
    cleaned_tweets = []
    
    tweets = json.loads(tweets_str)
    for tweet in tweets:
        # print(f'tweet\n{tweet}')

        tweet_id = tweet["id"]
        
        created_at = tweet["created_at"]
        final_created_at = created_at

        poster_username = tweet["_data"]["core"]["user_results"]["result"]["legacy"]["screen_name"]
        final_poster_username = poster_username
        
        #TODO: See why full text is incomplete
        full_text = tweet["full_text"].strip()
        full_text_wo_rt = re.sub(r'RT @\w+:', '', full_text)
        full_text_wo_url = re.sub(r'http\S+', '', full_text_wo_rt)
        final_full_text = full_text_wo_url
        
        media = tweet["media"]
        media_str = json.dumps(media)
        final_media = media_str
        
        media_post_urls = [media_item["expanded_url"] for media_item in media] if media else "-"
        media_post_urls_str = ' | '.join(media_post_urls)
        final_post_urls = media_post_urls_str
        
        media_content_urls = [media_item["media_url_https"] for media_item in media] if media else "-"
        media_content_urls_str = ' | '.join(media_content_urls)
        final_content_urls = media_content_urls_str

        cleaned_tweets.append(
            (
                tweet_id,
                final_created_at,
                final_poster_username,
                final_full_text,
                final_post_urls,
                final_content_urls
            )
        )

    return cleaned_tweets

# Initialize twitter client
async def tweet_login():
    client = Client(
        language = 'en-US',
    )
    if os.path.exists('data/cookies.json'):
        client.load_cookies('data/cookies.json')
    else:
        await client.login(
            auth_info_1 = USERNAME,
            auth_info_2 = EMAIL,
            password = PASSWORD
        )
        client.save_cookies('data/cookies.json')

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

# Get user tweets
async def get_user_tweets(con, cur, user):
    cnt = 0
    all_tweets = []
    
    try:
        tweets = await user.get_tweets('Tweets')
        cnt += 1
        all_tweets.append(
            (
                cnt, 
                format_tweet_dump_data(tweets), 
                "Tweets", 
                tweets.next_cursor
            )
        )
        print(f'Tweets Count: {cnt}')
        
        # Check if we've hit the rate limit
        if len(all_tweets) % RATE_LIMIT == 0 and len(all_tweets) > 0:
            print(f"Reached rate limit. Waiting for {RESET_INTERVAL} seconds.")
            time.sleep(RESET_INTERVAL)
        
        while True:
            tweets = await tweets.next()

            if not tweets:
                break
            
            cnt += 1
            all_tweets.append(
                (
                    cnt, 
                    format_tweet_dump_data(tweets), 
                    "Tweets", 
                    tweets.next_cursor
                )
            )
            print(f'Tweets Count: {cnt}')
    
    except Exception as e:
        print(f"Error: {e}")

    return all_tweets

# Get user bookmarks
async def get_user_bookmarks(con, cur, client):
    cnt = 0
    all_bookmarks = []
    
    try:
        bookmarks = await client.get_bookmarks()
        cnt += 1
        all_bookmarks.append(
            (
                cnt, 
                format_tweet_dump_data(bookmarks), 
                "Bookmarks", 
                bookmarks.next_cursor
            )
        )
        print(f'Bookmarks Count: {cnt}')
        
        # Check if we've hit the rate limit
        if len(all_bookmarks) % RATE_LIMIT == 0 and len(all_bookmarks) > 0:
            print(f"Reached rate limit. Waiting for {RESET_INTERVAL} seconds.")
            time.sleep(RESET_INTERVAL)
        
        while True:
            bookmarks = await bookmarks.next()

            if not bookmarks:
                break
            
            cnt += 1
            all_bookmarks.append(
                (
                    cnt, 
                    format_tweet_dump_data(bookmarks), 
                    "Bookmarks", 
                    bookmarks.next_cursor
                )
            )
            print(f'Bookmarks Count: {cnt}')
    
    except Exception as e:
        print(f"Error: {e}")

    return all_bookmarks