import sqlite3

def get_db_connection(): #Para conectar a la base de datos
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # This allows fetching results as dictionaries
    return conn

