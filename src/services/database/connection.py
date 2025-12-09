import sqlite3

def get_connection():
    conn = sqlite3.connect("news_ai.db")
    return conn