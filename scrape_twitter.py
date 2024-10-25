import os
import asyncio
from dotenv import load_dotenv
from twit import tweet_login, tweet_user, get_user_tweets, get_user_bookmarks, clean_tweet_dump_data
from db import database_init, database_create_vec, database_create_tweet_dump, database_create_tweets, database_insert_dump_data, database_insert_data, database_select_tweet_dump

async def scrape_twitter_func():
    con, cur = database_init()
    database_create_vec(cur)
    database_create_tweets(cur)
    database_create_tweet_dump(cur)

    twitter_client = await tweet_login()

    user = await tweet_user(twitter_client)

    # Get list of user tweets
    user_tweets_list = await get_user_tweets(con, cur, user)
    for tweet in user_tweets_list:
        database_insert_dump_data(con = con, cur = cur, data = tweet)

    # Get list of user bookmarks
    user_bookmarks_list = await get_user_bookmarks(con, cur, twitter_client)
    for bookmark in user_bookmarks_list:
        database_insert_dump_data(con = con, cur = cur, data = bookmark)
    
    # Clean the list of tweet data containing JSON strings
    tweet_dump_data = database_select_tweet_dump(cur)
    for tweet_data in tweet_dump_data:
        # Load the strings into JSON and then pick paramters and append to list 
        cleaned_tweet_dump_data = clean_tweet_dump_data(tweet_data[1])

        for cleaned_tweet in cleaned_tweet_dump_data:
            database_insert_data(con = con, cur = cur, data = cleaned_tweet)
    
    con.close()

if __name__ == "__main__":
    asyncio.run(scrape_twitter_func())