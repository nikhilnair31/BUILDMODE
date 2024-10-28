import numpy as np
from db import (
    database_init
)
from api import (
    replicate_embedding
)
from helper import (
    serialize_f32
)

con, cur = database_init()

def build_new_vec_table():
    cur.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS VECS3
        USING vec0(
            ID INTEGER PRIMARY KEY,
            EMBEDDING FLOAT[768]
        );
    """)

def select_tweet_data():
    cur.execute(
        f"""
        SELECT ID, FULL_TEXT, MEDIA_CONTENT_URLS
        FROM TWEETS
        """
    )
    output = cur.fetchall()
    return output

def database_insert_vec(con, cur, data):
    cur.execute(
        """
        INSERT OR REPLACE INTO VECS3 (ID, EMBEDDING) 
        VALUES (?, ?);
        """, 
        data
    )
    con.commit()

def run(output):
    print('Start embedding...')

    for row in output: 
        try:
            embedding_vec = []

            tweet_id, tweet_text, tweet_img_url = row
            print(f'{tweet_id} | {tweet_text[:25]}... | {tweet_img_url[:25]}...')
            
            if tweet_img_url == '-':
                embedding = replicate_embedding(
                    "andreasjansson/clip-features:75b33f253f7714a281ad3e9b28f63e3232d583716ef6718f2e46641077ea040a",
                    {"inputs": tweet_text}
                )[0]["embedding"]
                embedding_vec.append(embedding)
            else:
                for media_url in tweet_img_url.split(' | '):
                    vec = replicate_embedding(
                        "andreasjansson/clip-features:75b33f253f7714a281ad3e9b28f63e3232d583716ef6718f2e46641077ea040a",
                        {"inputs": media_url}
                    )[0]["embedding"]
                    embedding_vec.append(vec)
            
            print(f'shape of embedding_vec: {np.shape(embedding_vec)}')
            if isinstance(embedding_vec[0], list):
                embedding_vec_avg = np.average(np.array(embedding_vec), axis=0)
            else:
                embedding_vec_avg = embedding_vec
            print(f'shape of embedding_vec_avg: {np.shape(embedding_vec_avg)}')
            
            embedding_vec_ser = serialize_f32(embedding_vec_avg)
            
            database_insert_vec(con = con, cur = cur, data = (tweet_id, embedding_vec_ser))

        except Exception as e:
            print(e)
            continue

    print('Done embedding!')

if __name__ == '__main__':
    build_new_vec_table()
    rows = select_tweet_data()
    run(rows)