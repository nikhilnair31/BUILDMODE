import os
import sqlite3
import sqlite_vec
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv('DB_PATH')

# Initialize sqlite client
def database_init():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    
    con.enable_load_extension(True)
    sqlite_vec.load(con)
    con.enable_load_extension(False)
    sqlite_version, vec_version = con.execute(
        "select sqlite_version(), vec_version()"
    ).fetchone()
    # print(
    #     f'\n###########################################\n',
    #     f"sqlite_version={sqlite_version}, vec_version={vec_version}",
    #     f'\n###########################################\n',
    #     sep='\n'
    # )

    return con, cur
    
def database_vec_create(cur):
    cur.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS VECS
        USING vec0(
            ID INTEGER PRIMARY KEY,
            EMBEDDING FLOAT[1024] DISTANCE_METRIC = COSINE
        );
    """)

def database_tweets_create(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS 
        TWEETS (
            ID INTEGER PRIMARY KEY, 
            CREATED_AT_DATETIME TEXT, 
            FULL_TEXT TEXT, 
            MEDIA TEXT,
            MEDIA_URL_HTTPSS_STR TEXT
        );
    """)

# Insert data into sqlite client
def database_insert_tweet(con, cur, data):
    cur.execute(
        """
        INSERT OR IGNORE INTO TWEETS (ID, CREATED_AT_DATETIME, FULL_TEXT, MEDIA, MEDIA_URL_HTTPSS_STR) 
        VALUES (?, ?, ?, ?, ?);
        """, 
        data
    )
    con.commit()

# Insert data into sqlite client
def database_insert_vec(con, cur, data):
    cur.execute(
        """
        INSERT OR REPLACE INTO VECS (ID, EMBEDDING) 
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

# Select data into sqlite client
def database_select_tweet(cur):
    cur.execute('''SELECT * FROM TWEETS''')
    output = cur.fetchall()
    
    return output