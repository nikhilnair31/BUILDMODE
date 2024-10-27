import numpy as np
from db import (
    database_init
)
from api import (
    replicate_embedding
)
from helper import (
    serialize_f32,
    print_select_rows
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
    
    input_dict = {"inputs": query}
    query_vec = replicate_embedding(input_dict)[0]["embedding"]
    query_vec_serialized = [serialize_f32(query_vec)]
    count = 10
    
    similar_tweets_rows = database_select_vec(cur, query_vec_serialized, count)
    print(similar_tweets_rows)