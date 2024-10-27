import re
from helper import serialize_f32
from db import database_init, database_select_tweet, database_insert_vec
from api import replicate_embedding

def set_embdedding_func(con, cur):
    output = database_select_tweet(cur)

    for row in output: 
        try:
            embedding_vec = []
            input_dict = {}

            tweet_id, tweet_text, tweet_img_url = row
            
            if tweet_img_url == '-':
                embedding_vec = replicate_embedding(
                    "daanelson/imagebind:0383f62e173dc821ec52663ed22a076d9c970549c209666ac3db181618b7a304",
                    {"modality": "text", "text_input": tweet_text}
                )
            else:
                for media_url in tweet_img_url.split(' | '):
                    vec = replicate_embedding(
                        "daanelson/imagebind:0383f62e173dc821ec52663ed22a076d9c970549c209666ac3db181618b7a304",
                        input_dict = {"modality": "vision", "input": media_url}
                    )
                    embedding_vec.append(vec)
            
            # Handle averaging if there are multiple vectors (e.g., multiple media files)
            if isinstance(embedding_vec[0], list):
                embedding_vec_avg = np.average(np.array(embedding_vec), axis=0)
            else:
                embedding_vec_avg = embedding_vec
            
            embedding_vec_ser = serialize_f32(embedding_vec_avg)
            
            # Insert data into the database
            database_insert_vec(con = con, cur = cur, data = (tweet_id, embedding_vec_ser))

        except Exception as e:
            print(e)
            continue
    
    print('Done embedding!')