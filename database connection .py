import sqlite3
import os

def get_db_connection():
    """
    Establishes a connection to the SQLite database.
    
    If the database file 'social_media.db' does not exist, it will be created.
    Returns the connection object.
    """
    # Define the database file name
    db_file = 'social_media.db'
    
    # Check if the database file exists to provide a helpful message
    is_new_db = not os.path.exists(db_file)
    
    try:
        # Connect to the database. It will be created if it doesn't exist.
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row  # This allows access to columns by name
        
        if is_new_db:
            print(f"Database '{db_file}' created successfully.")
        else:
            print(f"Connection to existing database '{db_file}' successful.")
            
        return conn
        
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None

def create_users_table(conn):
    """
    Creates a 'users' table in the database if it doesn't already exist.
    
    Args:
        conn: The database connection object.
    """
    if conn is None:
        print("Cannot create table. No database connection.")
        return
    
    try:
        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()
        
        # SQL command to create the 'users' table
        sql_command = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Execute the SQL command
        cursor.execute(sql_command)
        
        # Commit the changes to the database
        conn.commit()
        
        print("Table 'users' created or verified successfully.")
        
    except sqlite3.Error as e:
        print(f"An error occurred while creating the table: {e}")

if __name__ == '__main__':
    # Get a database connection
    db_conn = get_db_connection()
    
    if db_conn:
        # Create the 'users' table
        create_users_table(db_conn)
        
        # Always close the connection when you're done
        db_conn.close()
        print("Database connection closed.")
