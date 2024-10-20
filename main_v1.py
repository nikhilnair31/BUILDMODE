import os
import sqlite3
import asyncio
from twikit import Client
from dotenv import load_dotenv

load_dotenv()

USER_SCREEN_NAME = os.get.environ('USER_SCREEN_NAME')
USERNAME = os.get.environ('USERNAME')
EMAIL = os.get.environ('EMAIL')
PASSWORD = os.get.environ('PASSWORD')
print(
    f'USER_SCREEN_NAME: {USER_SCREEN_NAME}',
    f'USERNAME: {USERNAME}',
    f'EMAIL: {EMAIL}',
    f'PASSWORD: {PASSWORD}',
    f'\n###########################################\n',
    sep='\n'
)

con = sqlite3.connect("data/tweets.db")
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS tweets(id INTEGER UNIQUE, created_at_datetime, full_text, media_url_httpss_str)")

async def download_media():
    tweet = await client.get_tweet_by_id('...')

    for i, media in enumerate(tweet.media):
        media_url = media.get('media_url_https')
        extension = media_url.rsplit('.', 1)[-1]

        response = await client.get(media_url, headers=client._base_headers)

        with open(f'media_{i}.{extension}', 'wb') as f:
            f.write(response.content)

async def main():
    # Initialize client
    client = Client(
        language = 'en-US',
    )
    await client.login(
        auth_info_1 = USERNAME,
        auth_info_2 = EMAIL,
        password = PASSWORD
    )

    ###########################################

    # Get user by screen name
    user = await client.get_user_by_screen_name(USER_SCREEN_NAME)
    # Access user attributes
    print(
        f'id: {user.id}',
        f'name: {user.name}',
        f'followers: {user.followers_count}',
        f'tweets count: {user.statuses_count}',
        f'\n###########################################\n',
        sep='\n'
    )

    ###########################################

    # Get user tweets
    user_tweets = await user.get_tweets('Tweets', count=1)
    for tweet in user_tweets:
        tweet_id = tweet.id
        created_at_datetime = tweet.created_at_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
        full_text = tweet.full_text.strip()
        media_url_httpss = [media_item["media_url_https"] for media_item in tweet.media] if tweet.media else "-"
        media_url_httpss_str = ' | '.join(media_url_httpss)

        # Access tweet attributes
        print(
            # f'id: {tweet.id}',
            f'full_text: {full_text}',
            f'created_at_datetime: {created_at_datetime}',
            f'media_url_httpss_str: {media_url_httpss_str}',
            # f'media: {tweet.media}',
            # f'user: {tweet.user}',
            # f'text: {tweet.text}',
            # f'in_reply_to: {tweet.in_reply_to}',
            # f'is_quote_status: {tweet.is_quote_status}',
            # f'retweeted_tweet: {tweet.retweeted_tweet}',
            # f'media_url_https: {tweet.media[0].media_url_https}' if tweet.media else "-",
            # f'media_url_https: {tweet["media"][0]["media_url_https"]}' if tweet.media in tweet and tweet["media"] else "-"
            # f'thumbnail_title: {tweet.thumbnail_title}',
            # f'thumbnail_url: {tweet.thumbnail_url}',
            # f'urls: {tweet.urls}',
            f'\n',
            sep='\n'
        )
        
        cur.execute(
            """INSERT INTO tweets(id, created_at_datetime, full_text, media_url_httpss_str) 
            VALUES (?, ?, ?, ?);""", 
            (tweet_id, created_at_datetime, full_text, media_url_httpss_str)
        )
        con.commit()

    # # Get more tweets
    # more_user_tweets = await user_tweets.next()
    # for tweet in more_user_tweets:
    #     print(tweet)

asyncio.run(main())