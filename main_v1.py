import os
import sqlite3
import asyncio
from twikit import Client
from dotenv import load_dotenv

load_dotenv()

USER_SCREEN_NAME = os.environ.get('USER_SCREEN_NAME')
USERNAME = os.environ.get('USERNAME')
EMAIL = os.environ.get('EMAIL')
PASSWORD = os.environ.get('PASSWORD')
print(
    f'USER_SCREEN_NAME: {USER_SCREEN_NAME}',
    f'USERNAME: {USERNAME}',
    f'EMAIL: {EMAIL}',
    f'PASSWORD: {PASSWORD}',
    f'\n###########################################\n',
    sep='\n'
)

async def download_media():
    tweet = await client.get_tweet_by_id('...')

    for i, media in enumerate(tweet.media):
        media_url = media.get('media_url_https')
        extension = media_url.rsplit('.', 1)[-1]

        response = await client.get(media_url, headers=client._base_headers)

        with open(f'media_{i}.{extension}', 'wb') as f:
            f.write(response.content)

# Initialize sqlite client
def database_init():
    con = sqlite3.connect("data/tweets.db")
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS 
        tweets(
            id INTEGER UNIQUE, 
            created_at_datetime TEXT, 
            full_text TEXT, 
            media_url_httpss_str TEXT
        )
    """)
    return con, cur
# Insert data into sqlite client
def database_insert_tweet(con, cur, data):
    cur.execute(
        """
        INSERT INTO tweets(id, created_at_datetime, full_text, media_url_httpss_str) 
        VALUES (?, ?, ?, ?);
        """, 
        data
    )
    con.commit()

# Initialize twitter client
async def tweet_login():
    client = Client(
        language='en-US',
    )
    await client.login(
        auth_info_1=USERNAME,
        auth_info_2=EMAIL,
        password=PASSWORD
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

        # Insert data into the database
        database_insert_tweet(
            con=con,
            cur=cur,
            data=(tweet_id, created_at_datetime, full_text, media_url_httpss_str)
        )

async def main():
    # Initialize the database
    con, cur = database_init()

    # Login to Twitter and get the client
    client = await tweet_login()

    # Get user by screen name
    user = await tweet_user(client)

    # Fetch and store the user's tweets
    await get_user_tweets(con, cur, user)

    # Optionally download media for a specific tweet
    # await download_media(client, tweet_id)

    # Close the database connection
    con.close()

asyncio.run(main())