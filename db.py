import os
import sqlite3
import sqlite_vec
from dotenv import load_dotenv

load_dotenv(override=True)

DB_PATH = os.getenv('DB_PATH')

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
            CREATED_AT TEXT, 
            POSTER_USERNAME TEXT,
            FULL_TEXT TEXT,
            MEDIA_POST_URLS TEXT,
            MEDIA_CONTENT_URLS TEXT
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

def database_create_github_user(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS 
        GIT_USER (
            USERNAME TEXT PRIMARY KEY, 
            LANGUAGE_COUNT TEXT,
            TECHNOLOGIES TEXT,
            REPO_EXPLAINERS TEXT,
            REPOS_SUMMARY TEXT
        );
    """)

def database_create_github_repo(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS 
        GIT_REPOS (
            ID INTEGER PRIMARY KEY, 
            NAME TEXT, 
            CREATED_AT TEXT,
            UPDATED_AT TEXT,
            LANGUAGES TEXT,
            TECHNOLOGIES TEXT,
            REPO_DESCRIPTION TEXT,
            REPO_README TEXT,
            EXPLAINER_TXT TEXT,
            COMMIT_CNT INTEGER
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
        INSERT OR IGNORE 
        INTO 
        TWEETS (
            ID, 
            CREATED_AT,
            POSTER_USERNAME,
            FULL_TEXT, 
            MEDIA_POST_URLS, 
            MEDIA_CONTENT_URLS
        ) 
        VALUES (?, ?, ?, ?, ?, ?);
        """, 
        data
    )
    con.commit()

def database_insert_vec(con, cur, data):
    cur.execute(
        """
        INSERT OR IGNORE INTO VECS (ID, EMBEDDING) 
        VALUES (?, ?);
        """, 
        data
    )
    con.commit()

def database_insert_github_user(con, cur, data):
    cur.execute(
        """
        INSERT OR REPLACE 
        INTO 
        GIT_USER (
            USERNAME, 
            LANGUAGE_COUNT,
            TECHNOLOGIES,
            REPO_EXPLAINERS,
            REPOS_SUMMARY
        ) 
        VALUES (?, ?, ?, ?, ?);
        """, 
        data
    )
    con.commit()
    
def database_insert_github_repo(con, cur, data):
    cur.execute(
        """
        INSERT OR REPLACE 
        INTO 
        GIT_REPOS (
            ID, 
            NAME, 
            CREATED_AT,
            UPDATED_AT,
            LANGUAGES,
            TECHNOLOGIES,
            REPO_DESCRIPTION,
            REPO_README,
            EXPLAINER_TXT,
            COMMIT_CNT
        ) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, 
        data
    )
    con.commit()

#endregion

#region Select data

def database_select_tweet_dump(cur):
    cur.execute(
        f'''
        SELECT * 
        FROM TWEET_DUMP
        '''
    )
    output = cur.fetchall()
    
    return output

def database_select_tweet(cur):
    cur.execute(
        f"""
        SELECT * 
        FROM TWEETS
        WHERE ID NOT IN (SELECT ID FROM VECS)
        """
    )
    output = cur.fetchall()
    
    return output
    
def database_select_vec(cur, query_vec_serialized, cnt):
    cur.execute(
        f"""
        SELECT T.ID, T.FULL_TEXT, T.MEDIA_CONTENT_URL, T.MEDIA_CONTENT_URL
        FROM TWEETS T
        INNER JOIN (
            SELECT ID
            FROM VECS
            WHERE EMBEDDING MATCH ? AND K = {cnt}
            ORDER BY DISTANCE ASC
        ) V
        ON T.ID = V.ID
        """,
        query_vec_serialized,
    )
    rows = cur.fetchall()
    
    return rows

def database_select_tweet_wo_media(cur):
    cur.execute(
        f'''
        SELECT POSTER_USERNAME, ID
        FROM TWEETS
        WHERE MEDIA_CONTENT_URLS = "-"
        '''
    )
    output = cur.fetchall()
    
    return output

#endregion

#region Update data

def database_update_data(cur):
    cur.execute(
        """
        UPDATE TWEETS
        SET FULL_TEXT = ? AND MEDIA_CONTENT_URLS = ?
        WHERE ID = ?;
        """, 
        data
    )
    con.commit()

#endregion