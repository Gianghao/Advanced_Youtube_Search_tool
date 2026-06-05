import psycopg2

def get_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="users",
        user="postgres",
        password="passwort",
        port="5432"
    )
    return conn