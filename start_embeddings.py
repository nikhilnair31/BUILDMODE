import re
import numpy as np
from helper import serialize_f32
from db import database_init, database_select_tweet, database_insert_vec
from api import replicate_init, replicate_embedding

def set_embdedding(replicate_client, con, cur):
    output = database_select_tweet(cur)

    for row in output: 
        embedding_vec = []
        input_dict = {}

        tweet_id, tweet_date, tweet_text, tweet_media_str, tweet_img_url = row
        full_text = tweet_text.strip()
        full_text_wo_rt = re.sub(r'RT @\w+:', '', full_text)
        full_text_wo_url = re.sub(r'http\S+', '', full_text_wo_rt)
        print(
            f'tweet_id: {tweet_id}',
            f'tweet_date: {tweet_date}',
            f'tweet_text: {full_text_wo_url}',
            f'tweet_media_str: {tweet_media_str}',
            f'tweet_img_url: {tweet_img_url}',
            f'\n',
            sep='\n'
        )
        
        if tweet_img_url == '-':
            input_dict = {"modality": "text", "text_input": full_text_wo_url}
            embedding_vec = replicate_embedding(replicate_client, input_dict)
        else:
            for media in tweet_img_url.split(' | '):
                print(f'media: {media}')
                input_dict = {"modality": "vision", "input": media}
                vec = replicate_embedding(replicate_client, input_dict)
                embedding_vec.append(vec)
        print(f'embedding_vec shape: {np.shape(embedding_vec)}')
        
        # Handle averaging if there are multiple vectors (e.g., multiple media files)
        if isinstance(embedding_vec[0], list):
            embedding_vec_avg = np.average(np.array(embedding_vec), axis=0)
        else:
            embedding_vec_avg = embedding_vec
        print(f'embedding_vec_avg shape: {np.shape(embedding_vec_avg)}')
        
        embedding_vec_ser = serialize_f32(embedding_vec_avg)
        
        # Insert data into the database
        database_insert_vec(con = con, cur = cur, data = (tweet_id, embedding_vec_ser))

if __name__ == "__main__":
    con, cur = database_init()
    replicate_client = replicate_init()
    set_embdedding(replicate_client, con, cur)