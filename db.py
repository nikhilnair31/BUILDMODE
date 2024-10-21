import os
import sqlite3
import sqlite_vec
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv('DB_PATH')

# Initialize sqlite client
def database_init():
    con = sqlite3.connect(DB_PATH)
    
    con.enable_load_extension(True)
    sqlite_vec.load(con)
    con.enable_load_extension(False)
    sqlite_version, vec_version = con.execute(
        "select sqlite_version(), vec_version()"
    ).fetchone()
    print(
        f"sqlite_version={sqlite_version}, vec_version={vec_version}",
        f'\n###########################################\n',
        sep='\n'
    )
    
    cur = con.cursor()
    cur.execute("""
        CREATE VIRTUAL TABLE VECS
        USING vec0(
            ID INTEGER PRIMARY KEY,
            EMBEDDING FLOAT[1024] DISTANCE_METRIC = COSINE
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS 
        TWEETS (
            ID INTEGER UNIQUE, 
            CREATED_AT_DATETIME TEXT, 
            FULL_TEXT TEXT, 
            MEDIA_URL_HTTPSS_STR TEXT
        );
    """)

    return con, cur

# Insert data into sqlite client
def database_insert_tweet(con, cur, data):
    cur.execute(
        """
        INSERT INTO TWEETS (ID, CREATED_AT_DATETIME, FULL_TEXT, MEDIA_URL_HTTPSS_STR) 
        VALUES (?, ?, ?, ?);
        """, 
        data
    )
    con.commit()

# Insert data into sqlite client
def database_insert_vec(con, cur, data):
    cur.execute(
        """
        INSERT INTO VECS (ID, EMBEDDING) 
        VALUES (?, ?);
        """, 
        data
    )
    con.commit()

# Update data into sqlite client
def database_update_tweet(con, cur, tweet_id, vec_val):
    cur.execute(
        f"""
        UPDATE tweets 
        SET embedding = ?
        WHERE id = ?;
        """,
        (vec_val, tweet_id)
    )
    con.commit()