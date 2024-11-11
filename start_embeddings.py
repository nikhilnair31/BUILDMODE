import re
import numpy as np
from helper import serialize_f32
from db import database_init, database_select_tweet, database_insert_vec
from api import replicate_embedding

def get_avg_vec(tweet_text, tweet_img_url):
    model_name = "daanelson/imagebind:0383f62e173dc821ec52663ed22a076d9c970549c209666ac3db181618b7a304"

    # If no image, generate text embedding
    if tweet_img_url == '-':
        try:
            return replicate_embedding(
                model_name,
                input_dict={"modality": "text", "text_input": tweet_text}
            )
        except Exception as e:
            print(f"Error generating text embedding: {e}")
            return None
    
    # If image URLs are provided
    else:
        try:
            # Split multiple image URLs and generate embeddings for each
            embedding_vec = []
            for media_url in tweet_img_url.split(' | '):
                vec = replicate_embedding(
                    model_name,
                    input_dict={"modality": "vision", "input": media_url}
                )
                embedding_vec.append(vec)
            
            # Return average embedding if multiple images
            return np.average(np.array(embedding_vec), axis=0)
        
        except Exception as e:
            print(f"Error generating image embedding: {e}")
            return None

def set_embdedding_func(con, cur):
    output = database_select_tweet(cur)

    for row in output: 
        try:
            tweet_id, tweet_text, tweet_img_url = row

            embedding_vec = get_avg_vec(tweet_text, tweet_img_url)
            
            if embedding_vec is not None:
                # Handle averaging if there are multiple vectors (e.g., multiple media files)
                if isinstance(embedding_vec[0], list):
                    embedding_vec_avg = np.average(np.array(embedding_vec), axis=0)
                else:
                    embedding_vec_avg = embedding_vec
            
                embedding_vec_ser = serialize_f32(embedding_vec_avg)
                
                # Insert data into the database
                database_insert_vec(con = con, cur = cur, data = (tweet_id, embedding_vec_ser))

        except Exception as e:
            print(f"Error processing tweet {tweet_id}: {e}")
            continue
    
    print('Done embedding!')