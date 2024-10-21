from api import replicate_init, replicate_embedding
from db import database_init
from helper import serialize_f32

replicate_client = replicate_init()
con, cur = database_init()

query = input("Enter your query: ")
input_dict = {"modality": "text", "text_input": query}
query_vec = replicate_embedding(replicate_client, input_dict)

rows = cur.execute(
    """
    SELECT *
    FROM tweets
    WHERE embedding MATCH ?
    ORDER BY distance
    LIMIT 2
    """,
    [serialize_f32(query_vec)],
).fetchall()

print(rows)