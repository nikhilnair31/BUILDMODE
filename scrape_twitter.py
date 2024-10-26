import os
import json
import asyncio
from dotenv import load_dotenv
from scrape_playwright import scrape_tweet
from twit import tweet_login, tweet_user, get_user_tweets, get_user_bookmarks, clean_tweet_dump_data
from db import (database_init, database_create_vec, database_create_tweet_dump, database_create_tweets, database_insert_dump_data, database_insert_data, database_select_tweet_dump, database_select_tweet_wo_media)

async def scrape_twitter_func(con, cur):
    database_create_vec(cur)
    database_create_tweets(cur)
    database_create_tweet_dump(cur)

    twitter_client = await tweet_login()

    user = await tweet_user(twitter_client)

    # Get list of user tweets
    user_tweets_list = await get_user_tweets(con, cur, user)
    print(f'Got User tweets')
    for tweet in user_tweets_list:
        database_insert_dump_data(con = con, cur = cur, data = tweet)
    print(f'Inserted User tweets!')

    # Get list of user bookmarks
    user_bookmarks_list = await get_user_bookmarks(con, cur, twitter_client)
    print(f'Got User bookmarks')
    for bookmark in user_bookmarks_list:
        database_insert_dump_data(con = con, cur = cur, data = bookmark)
    print(f'Inserted User bookmarks!')

    # Clean the list of tweet data containing JSON strings
    tweet_dump_data = database_select_tweet_dump(cur)
    print(f'Pulled User tweets dump data')
    for tweet_data in tweet_dump_data:
        # Load the strings into JSON and then pick paramters and append to list 
        tweet_data_json = tweet_data[1]
        cleaned_tweet_dump_data = clean_tweet_dump_data(tweet_data_json)

        for cleaned_tweet in cleaned_tweet_dump_data:
            database_insert_data(con = con, cur = cur, data = cleaned_tweet)
    print(f'Cleaned and Inserted tweets!')

def scraping_to_update_data_wo_media(con, cur):
    tweets_wo_media_list = database_select_tweet_wo_media(cur)
    for tweet_wo_media in tweets_wo_media_list:
        # Feed this into Playwright to pull missing information
        poster_username, post_id = tweet_wo_media
        post_url = f"https://x.com/{poster_username}/status/{post_id}"
        print(
            f'poster_username: {poster_username}',
            f'post_id: {post_id}', 
            f'post_url: {post_url}',
            sep='\n'
        )
        
        try:
            new_post_data = scrape_tweet(post_url)
            print(f'new_post_data: {new_post_data}')

            full_text, media_content_urls_str = new_post_data
            update_post_data = (post_id, full_text, media_content_urls_str)
            print(f'update_post_data: {update_post_data}')
            database_update_data(con = con, cur = cur, data = update_post_data)
        
        except Exception as e:
            print(f'Error: {e}\n')
            continue