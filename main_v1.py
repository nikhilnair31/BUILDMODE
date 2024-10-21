import os
import asyncio
import numpy as np
from dotenv import load_dotenv
from helper import serialize_f32
from twit import tweet_login, tweet_user, get_user_tweets
from db import database_init, database_insert_tweet, database_update_tweet
from api import replicate_init, replicate_embedding

def set_embdedding(replicate_client, con, cur):
    cur.execute('''SELECT * FROM tweets''') 
    output = cur.fetchall()

    for row in output: 
        embedding_vec = []
        input_dict = {}

        tweet_id, tweet_date, tweet_text, tweet_media, _ = row
        print(
            f'tweet_id: {tweet_id}',
            f'tweet_date: {tweet_date}',
            f'tweet_text: {tweet_text}',
            f'tweet_media: {tweet_media}',
            f'\n',
            sep='\n'
        )
        
        if tweet_media == '-':
            input_dict = {"modality": "text", "text_input": tweet_text}
            embedding_vec = replicate_embedding(replicate_client, input_dict)
        else:
            for media in tweet_media.split(' | '):
                print(f'media: {media}')
                input_dict = {"modality": "vision", "input": media}
                vec = replicate_embedding(replicate_client, input_dict)
                embedding_vec.append(vec)
        print(f'embedding_vec shape: {embedding_vec.shape}')
        
        # Handle averaging if there are multiple vectors (e.g., multiple media files)
        if isinstance(embedding_vec[0], list):
            embedding_vec_avg = np.average(np.array(embedding_vec), axis=0)
        else:
            embedding_vec_avg = embedding_vec
        print(f'embedding_vec_avg shape: {embedding_vec_avg.shape}')
        
        embedding_vec_ser = serialize_f32(embedding_vec_avg)
        print(f'embedding_vec_ser shape: {embedding_vec_ser.shape}\n')
        
        # Insert data into the database
        database_insert_vec(con = con, cur = cur, tweet_id = tweet_id, vec_val = embedding_vec_ser)

async def main():
    # Initialize the database
    con, cur = database_init()

    # Get client for Replicate
    replicate_client = replicate_init()

    # Login to Twitter and get the client
    twitter_client = await tweet_login()

    # Get user by screen name
    user = await tweet_user(twitter_client)

    # Fetch and store the user's tweets
    user_tweets_list = await get_user_tweets(con, cur, user)
    for tweet in user_tweets_list:
        database_insert_tweet(con = con, cur = cur, data = tweet)

    set_embdedding(replicate_client, con, cur)
    
    # Close the database connection
    con.close()

if __name__ == "__main__":
    # Run the main async function
    asyncio.run(main())