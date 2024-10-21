import os
import asyncio
from dotenv import load_dotenv
from twit import tweet_login, tweet_user, get_user_tweets
from db import database_init, database_vec_create, database_tweets_create, database_insert_tweet

async def main():
    con, cur = database_init()
    # database_vec_create(cur)
    database_tweets_create(cur)

    twitter_client = await tweet_login()

    user = await tweet_user(twitter_client)

    user_tweets_list = await get_user_tweets(con, cur, user)
    for tweet in user_tweets_list:
        database_insert_tweet(con = con, cur = cur, data = tweet)
    
    con.close()

if __name__ == "__main__":
    asyncio.run(main())