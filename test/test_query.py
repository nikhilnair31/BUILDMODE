from api import replicate_embedding, openai_chat, anthropic_chat
from db import database_init
from helper import serialize_f32

con, cur = database_init()

query = f"""
Give me top 3 video game ideas. I'm a solo Unity game developer and have a weekend to build this for a game jam. Focus on unique shooter gameplay mechanics. 
"""
input_dict = {"modality": "text", "text_input": query}
query_vec = replicate_embedding(input_dict)

rows = cur.execute(
    """
    SELECT T.ID, T.FULL_TEXT, T.MEDIA_URL_HTTPSS_STR
    FROM TWEETS T
    INNER JOIN (
        SELECT ID
        FROM VECS
        WHERE EMBEDDING MATCH ? AND K = 100
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

anthropic_chat(
    model = "claude-3-5-sonnet-20241022",
    messages = rows,
    system = query 
)