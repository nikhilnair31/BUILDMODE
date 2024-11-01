import os
import re
import json
import time
from twikit import Client
from dotenv import load_dotenv
from helper import serialize_clean

load_dotenv()

RATE_LIMIT = int(os.getenv('TWITTER_RATE_LIMIT'))
RESET_INTERVAL = int(os.getenv('TWITTER_RESET_INTERVAL'))
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
# Append a tweet to the collection list with proper formatting.
async def append_tweet_to_list(tweets, all_tweets, cnt, tweet_type):
    all_tweets.append(
        (
            cnt, 
            format_tweet_dump_data(tweets), 
            tweet_type, 
            tweets.next_cursor
        )
    )
    print(f'Tweets Count: {cnt}')
    
    # Handle rate limiting
    if len(all_tweets) % RATE_LIMIT == 0 and len(all_tweets) > 0:
        print(f"Reached rate limit. Waiting for {RESET_INTERVAL} seconds.")
        time.sleep(RESET_INTERVAL)
    
    return cnt + 1
# Check if any new tweet IDs are already in saved tweets
def check_for_saved_tweet_id(tweets, saved_ids):
    if len(saved_ids) > 0:
        # Access the results from the tweet object
        tweets_result = tweets.__dict__["_Result__results"]
        tweets_data = [serialize_clean(tweet) for tweet in tweets_result]

        # Get the tweet ID from the results
        extracted_ids = [int(tweet["id"]) for tweet in tweets_data]

        # Get the tweet ID from the results
        for tweet_id in extracted_ids:
            if tweet_id in saved_ids:
                print(f"Found duplicate tweet ID {tweet_id}. Skipping update.")
                return True
    
    print(f"Found NO duplicate tweet IDs")
    return False

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
async def get_user_tweets(con, cur, user, saved_ids):
    cnt = 0
    all_tweets = []
    
    try:
        tweets = await user.get_tweets('Tweets')

        # Append initial tweets
        cnt = await append_tweet_to_list(tweets, all_tweets, cnt, "Tweets")
        
        # Check if any new tweet IDs are already in saved tweets
        if check_for_saved_tweet_id(tweets, saved_ids):
            return all_tweets
        
        # Fetch remaining tweets
        while True:
            tweets = await tweets.next()
            
            if not tweets:
                break

            if check_for_saved_tweet_id(tweets, saved_ids):
                return all_tweets
            
            cnt = await append_tweet_to_list(tweets, all_tweets, cnt, "Tweets")
    
    except Exception as e:
        print(f"Error: {e}")

    return all_tweets

# Get user bookmarks
async def get_user_bookmarks(con, cur, client, saved_ids):
    cnt = 0
    all_bookmarks = []
    
    try:
        bookmarks = await client.get_bookmarks()

        # Append initial bookmarks
        cnt = await append_tweet_to_list(bookmarks, all_bookmarks, cnt, "Bookmarks")
        
        # Check if any new tweet IDs are already in saved 
        if check_for_saved_tweet_id(bookmarks, saved_ids):
            return all_bookmarks
        
        # Fetch remaining bookmarks
        while True:
            bookmarks = await bookmarks.next()
            
            if not bookmarks:
                break

            if check_for_saved_tweet_id(bookmarks, saved_ids):
                return all_bookmarks
            
            cnt = await append_tweet_to_list(bookmarks, all_bookmarks, cnt, "Bookmarks")
    
    except Exception as e:
        print(f"Error: {e}")

    return all_bookmarks