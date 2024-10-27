import re
from helper import serialize_f32
from db import database_init, database_select_tweet, database_insert_vec
from api import replicate_embedding

def set_embdedding_func(con, cur):
    output = database_select_tweet(cur)
    # print(f'output shape: {np.shape(output)}')

    for row in output: 
        try:
            embedding_vec = []
            input_dict = {}

            tweet_id, _, tweet_text, _, _, tweet_img_url = row
            
            if tweet_img_url == '-':
                input_dict = {"modality": "text", "text_input": tweet_text}
                embedding_vec = replicate_embedding(input_dict)
            else:
                for media in tweet_img_url.split(' | '):
                    input_dict = {"modality": "vision", "input": media}
                    vec = replicate_embedding(input_dict)
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