import sqlite3
import os
from datetime import datetime

DB_NAME = 'social_media.db'

def get_db_connection():
    """
    Establishes a connection to the SQLite database.
    Returns the connection object.
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row  # Access columns by name
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def setup_database(conn):
    """
    Creates the necessary 'users', 'posts', and 'post_reactions' tables.
    """
    if conn is None:
        return

    cursor = conn.cursor()

    # 1. Create a simplified 'users' table (needed for foreign keys)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE
        );
    """)

    # 2. Create the 'posts' table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
    """)

    # 3. Create the 'post_reactions' table
    # This tracks who liked/disliked which post, ensuring only one reaction per user per post.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS post_reactions (
            post_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            reaction_type TEXT NOT NULL, -- 'like' or 'dislike'
            reacted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (post_id, user_id),
            FOREIGN KEY (post_id) REFERENCES posts (id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            CHECK (reaction_type IN ('like', 'dislike'))
        );
    """)
    conn.commit()
    print("Database setup complete: users, posts, and post_reactions tables verified.")

def create_post(conn, user_id, content):
    """
    Inserts a new post into the 'posts' table.
    Returns the ID of the new post.
    """
    if conn is None:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO posts (user_id, content) VALUES (?, ?)",
            (user_id, content)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Error creating post: {e}")
        return None

def set_post_reaction(conn, post_id, user_id, reaction_type):
    """
    Handles a user's like or dislike action on a post.
    
    If a reaction already exists:
    1. If the new reaction is the same, it removes the reaction (toggle off).
    2. If the new reaction is different, it updates the existing reaction.
    If no reaction exists, it adds the new reaction.
    """
    if conn is None:
        return False

    if reaction_type not in ['like', 'dislike']:
        print("Invalid reaction type. Must be 'like' or 'dislike'.")
        return False

    try:
        cursor = conn.cursor()
        
        # 1. Check for an existing reaction by this user on this post
        cursor.execute(
            "SELECT reaction_type FROM post_reactions WHERE post_id = ? AND user_id = ?",
            (post_id, user_id)
        )
        existing_reaction = cursor.fetchone()

        if existing_reaction:
            # Existing reaction found
            existing_type = existing_reaction['reaction_type']
            
            if existing_type == reaction_type:
                # 2. Toggle off (remove) the reaction if it's the same type
                cursor.execute(
                    "DELETE FROM post_reactions WHERE post_id = ? AND user_id = ?",
                    (post_id, user_id)
                )
                action = f"Reaction '{reaction_type}' removed."
            else:
                # 3. Update the reaction if the type is different (e.g., changing like to dislike)
                cursor.execute(
                    "UPDATE post_reactions SET reaction_type = ?, reacted_at = CURRENT_TIMESTAMP WHERE post_id = ? AND user_id = ?",
                    (reaction_type, post_id, user_id)
                )
                action = f"Reaction changed to '{reaction_type}'."
        else:
            # 4. No existing reaction, insert the new one
            cursor.execute(
                "INSERT INTO post_reactions (post_id, user_id, reaction_type) VALUES (?, ?, ?)",
                (post_id, user_id, reaction_type)
            )
            action = f"Reaction '{reaction_type}' added."

        conn.commit()
        print(f"Post {post_id} - User {user_id}: {action}")
        return True

    except sqlite3.Error as e:
        print(f"Error setting post reaction: {e}")
        return False

def get_post_reaction_counts(conn, post_id):
    """
    Retrieves the total like and dislike counts for a specific post.
    """
    if conn is None:
        return {'likes': 0, 'dislikes': 0}

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT reaction_type, COUNT(*) as count
            FROM post_reactions
            WHERE post_id = ?
            GROUP BY reaction_type
            """,
            (post_id,)
        )
        
        counts = {'likes': 0, 'dislikes': 0}
        for row in cursor.fetchall():
            if row['reaction_type'] == 'like':
                counts['likes'] = row['count']
            elif row['reaction_type'] == 'dislike':
                counts['dislikes'] = row['count']
        
        return counts

    except sqlite3.Error as e:
        print(f"Error getting reaction counts: {e}")
        return {'likes': 0, 'dislikes': 0}

def mock_user_creation(conn, username, email):
    """Utility function to create mock users for testing."""
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO users (username, email) VALUES (?, ?)",
            (username, email)
        )
        conn.commit()
        # Return the user ID (can be retrieved this way after INSERT OR IGNORE)
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        return cursor.fetchone()['id']
    except sqlite3.Error as e:
        print(f"Error creating mock user: {e}")
        return None

# --- Demonstration and Testing ---

if __name__ == '__main__':
    # Initialize database
    conn = get_db_connection()
    if conn:
        setup_database(conn)

        # 1. Mock Users
        user1_id = mock_user_creation(conn, "testuser1", "user1@example.com")
        user2_id = mock_user_creation(conn, "testuser2", "user2@example.com")
        
        print(f"\nUser 1 ID: {user1_id}, User 2 ID: {user2_id}")

        # 2. User 1 creates a post
        post1_id = create_post(conn, user1_id, "Just finished my first Python social media module!")
        print(f"Post 1 created with ID: {post1_id}")
        
        # 3. User 1 (the post owner) likes their own post
        print("\n--- User 1 (owner) likes their post ---")
        set_post_reaction(conn, post1_id, user1_id, 'like')
        print("Counts:", get_post_reaction_counts(conn, post1_id))
        
        # 4. User 1 changes their mind and dislikes their post
        print("\n--- User 1 changes their reaction to dislike ---")
        set_post_reaction(conn, post1_id, user1_id, 'dislike')
        print("Counts:", get_post_reaction_counts(conn, post1_id))
        
        # 5. User 1 clicks dislike again (toggling it off)
        print("\n--- User 1 toggles dislike off ---")
        set_post_reaction(conn, post1_id, user1_id, 'dislike')
        print("Counts:", get_post_reaction_counts(conn, post1_id))
        
        # 6. User 2 reacts to the same post (to show multiple reactions are tracked)
        print("\n--- User 2 likes the post (showing multi-user support) ---")
        set_post_reaction(conn, post1_id, user2_id, 'like')
        print("Counts:", get_post_reaction_counts(conn, post1_id))
        
        # 7. User 1 likes their post again
        print("\n--- User 1 likes their post again ---")
        set_post_reaction(conn, post1_id, user1_id, 'like')
        print("Counts:", get_post_reaction_counts(conn, post1_id))

        # Cleanup
        conn.close()
        # os.remove(DB_NAME) # Uncomment to delete the database file after running
        print(f"\nDatabase '{DB_NAME}' closed.")
