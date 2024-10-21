from api import replicate_init, replicate_embedding
from db import database_init
from helper import serialize_f32

replicate_client = replicate_init()
con, cur = database_init()

query = f"""
models
"""
input_dict = {"modality": "text", "text_input": query}
query_vec = replicate_embedding(replicate_client, input_dict)

rows = cur.execute(
    """
    SELECT T.FULL_TEXT, T.MEDIA_URL_HTTPSS_STR
    FROM TWEETS T
    INNER JOIN (
        SELECT ID
        FROM VECS
        WHERE EMBEDDING MATCH ? AND K = 5
        ORDER BY DISTANCE ASC
    ) V
    ON T.ID = V.ID
    """,
    [serialize_f32(query_vec)],
).fetchall()

idx = 1
for row in rows:
    print(f'{idx}: {row[1] if row[1] != "-" else row[0]}\n')
    idx += 1