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
        CREATE TABLE IF NOT EXISTS 
        tweets(
            id INTEGER UNIQUE, 
            created_at_datetime TEXT, 
            full_text TEXT, 
            media_url_httpss_str TEXT,
            embedding float[1024]
        )
    """)

    return con, cur

# Insert data into sqlite client
def database_insert_tweet(con, cur, data):
    cur.execute(
        """
        INSERT INTO tweets(id, created_at_datetime, full_text, media_url_httpss_str) 
        VALUES (?, ?, ?, ?);
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