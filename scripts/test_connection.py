import psycopg2
import config

try:
    conn = psycopg2.connect(**config.DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT version();")
    print("Connected successfully!")
    print(cur.fetchone()[0])
    cur.close()
    conn.close()
except Exception as e:
    print("Connection failed:")
    print(e)
