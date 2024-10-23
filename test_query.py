from api import replicate_init, replicate_embedding, openai_init, openai_chat
from db import database_init
from helper import serialize_f32

openai_client = openai_init()
replicate_client = replicate_init()
con, cur = database_init()

query = f"""
ai productivity app for mobile with gradient visuals
"""
input_dict = {"modality": "text", "text_input": query}
query_vec = replicate_embedding(replicate_client, input_dict)

rows = cur.execute(
    """
    SELECT T.ID, T.FULL_TEXT, T.MEDIA_URL_HTTPSS_STR
    FROM TWEETS T
    INNER JOIN (
        SELECT ID
        FROM VECS
        WHERE EMBEDDING MATCH ? AND K = 10
        ORDER BY DISTANCE ASC
    ) V
    ON T.ID = V.ID
    """,
    [serialize_f32(query_vec)],
).fetchall()

idx = 1
for row in rows:
    print(
        f'idx: {idx} - id: {row[0]}',
        f'text: {row[1]}',
        f'urls: {row[2]}',
        f'-------------------------------------------------------',
        sep='\n'
    )
    idx += 1

openai_chat(openai_client, query, rows)