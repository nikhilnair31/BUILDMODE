import os
import sqlite3
import sqlite_vec
from dotenv import load_dotenv

load_dotenv(override=True)

DB_PATH = os.getenv('DB_PATH')
print(f'DB_PATH: {DB_PATH}')

#region Init

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

#endregion

#region Create tables     

def database_create_vec(cur):
    cur.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS VECS
        USING vec0(
            ID INTEGER PRIMARY KEY,
            EMBEDDING FLOAT[1024] DISTANCE_METRIC = COSINE
        );
    """)

def database_create_tweets(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS 
        TWEETS (
            ID INTEGER PRIMARY KEY, 
            CREATED_AT_DATETIME TEXT, 
            FULL_TEXT TEXT, 
            MEDIA TEXT,
            MEDIA_POST_URL TEXT,
            MEDIA_CONTENT_URL TEXT
        );
    """)

def database_create_tweet_dump(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS 
        TWEET_DUMP (
            CNT INTEGER, 
            TWEET_DUMP TEXT,
            TYPE TEXT,
            NEXT_CURSOR TEXT
        );
    """)

#endregion

#region Insert data

def database_insert_dump_data(con, cur, data):
    cur.execute(
        """
        INSERT OR IGNORE INTO TWEET_DUMP (CNT, TWEET_DUMP, TYPE, NEXT_CURSOR) 
        VALUES (?, ?, ?, ?);
        """, 
        data
    )
    con.commit()

def database_insert_data(con, cur, data):
    cur.execute(
        """
        INSERT OR IGNORE INTO TWEETS (ID, CREATED_AT_DATETIME, FULL_TEXT, MEDIA, MEDIA_POST_URL, MEDIA_CONTENT_URL) 
        VALUES (?, ?, ?, ?, ?, ?);
        """, 
        data
    )
    con.commit()

def database_insert_vec(con, cur, data):
    cur.execute(
        """
        INSERT OR REPLACE INTO VECS (ID, EMBEDDING) 
        VALUES (?, ?);
        """, 
        data
    )
    con.commit()

#endregion

#region Select data

def database_select_tweet_dump(cur):
    cur.execute('''SELECT * FROM TWEET_DUMP''')
    output = cur.fetchall()
    
    return output


def database_select_tweet(cur):
    cur.execute('''SELECT * FROM TWEETS''')
    output = cur.fetchall()
    
    return output

#endregion