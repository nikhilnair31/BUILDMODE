import os
from twikit import Client
from dotenv import load_dotenv

load_dotenv()

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
    user_tweet_list = []
    user_tweets = await user.get_tweets('Tweets', count=1)
    
    for tweet in user_tweets:
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
            f'\n',
            sep='\n'
        )
        
        user_tweet_list.append((tweet_id, created_at_datetime, full_text, media_url_httpss_str))

    return user_tweet_list