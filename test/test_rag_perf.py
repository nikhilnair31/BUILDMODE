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

def database_select_vec(cur, query_vec_serialized, cnt):
    cur.execute(
        f"""
        SELECT T.ID, T.FULL_TEXT
        FROM TWEETS T
        INNER JOIN (
            SELECT ID
            FROM VECS3
            WHERE EMBEDDING MATCH ? AND K = {cnt}
            ORDER BY DISTANCE ASC
        ) V
        ON T.ID = V.ID
        """,
        query_vec_serialized,
    )
    rows = cur.fetchall()
    
    return rows

if __name__ == '__main__':
    query = 'tamagochi mecha'
    
    # query_vec = replicate_embedding(
    #     "daanelson/imagebind:0383f62e173dc821ec52663ed22a076d9c970549c209666ac3db181618b7a304",
    #     {"modality": "text", "text_input": query}
    # )
    query_vec = replicate_embedding(
        "andreasjansson/clip-features:75b33f253f7714a281ad3e9b28f63e3232d583716ef6718f2e46641077ea040a",
        {"inputs": query}
    )
    query_vec = query_vec[0]["embedding"]

    query_vec_serialized = [serialize_f32(query_vec)]
    count = 10
    
    similar_tweets_rows = database_select_vec(cur, query_vec_serialized, count)
    for row in similar_tweets_rows:
        print(f'{row[0]} - {row[1][:50]}...')