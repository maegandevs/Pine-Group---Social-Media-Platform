import sqlite3
import datetime
# We assume database.py is in the same directory for connection functions
from database import get_db_connection, setup_database 

# --- Core Feature: Commenting on a Post ---

def add_comment(post_id, user_email, comment_text):
    """
    Adds a new comment to a specific post in the database.
    
    Args:
        post_id (int): The ID of the post to comment on.
        user_email (str): The email of the commenting user (used to find user_id).
        comment_text (str): The content of the comment.
        
    Returns:
        bool: True if the comment was added successfully, False otherwise.
    """
    # Basic input validation
    if not comment_text or not post_id or not user_email:
        print("Error: Missing comment text, post ID, or user email.")
        return False
        
    conn = get_db_connection()
    if conn is None:
        return False
        
    try:
        cursor = conn.cursor()
        
        # 1. Find the user_id from the user_email
        cursor.execute("SELECT id FROM users WHERE email = ?", (user_email,))
        user_row = cursor.fetchone()
        
        if user_row is None:
            print(f"Error: User with email '{user_email}' not found.")
            return False
            
        user_id = user_row['id']
        
        # 2. Check if the post exists
        cursor.execute("SELECT id FROM posts WHERE id = ?", (post_id,))
        if cursor.fetchone() is None:
            print(f"Error: Post with ID {post_id} not found.")
            return False
            
        # 3. Insert the new comment into the comments table
        cursor.execute("""
            INSERT INTO comments (post_id, user_id, comment_text, created_at)
            VALUES (?, ?, ?, ?)
        """, (post_id, user_id, comment_text, datetime.datetime.now().isoformat()))
        
        conn.commit()
        print(f"Success: Comment added by user {user_email} on post {post_id}.")
        return True
        
    except sqlite3.Error as e:
        print(f"An error occurred while adding the comment: {e}")
        return False
    finally:
        if conn:
            conn.close()

# --- Helper Functions for Demonstration ---

def add_mock_user(email, name="Mock User", password_hash="hashed_pw"):
    """Adds a mock user if they don't exist, for testing purposes."""
    conn = get_db_connection()
    if conn is None: return
    try:
        cursor = conn.cursor()
        # Use INSERT OR IGNORE to prevent errors if user already exists
        cursor.execute("INSERT OR IGNORE INTO users (email, password_hash, name) VALUES (?, ?, ?)", 
                       (email, password_hash, name))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error adding mock user: {e}")
    finally:
        if conn: conn.close()
        
def add_mock_post(user_email, content):
    """Adds a mock post and returns its ID."""
    conn = get_db_connection()
    if conn is None: return None
    try:
        cursor = conn.cursor()
        # Find the user_id
        cursor.execute("SELECT id FROM users WHERE email = ?", (user_email,))
        user_row = cursor.fetchone()
        if user_row is None: return None
        
        user_id = user_row['id']
        
        # Insert the post
        cursor.execute("""
            INSERT INTO posts (user_id, content, created_at) VALUES (?, ?, ?)
        """, (user_id, content, datetime.datetime.now().isoformat()))
        
        post_id = cursor.lastrowid # Get the ID of the newly inserted post
        conn.commit()
        return post_id
    except sqlite3.Error as e:
        print(f"Error adding mock post: {e}")
        return None
    finally:
        if conn: conn.close()

def get_post_and_comments(post_id):
    """Retrieves a post and all its comments for display."""
    conn = get_db_connection()
    if conn is None: return None
    
    result = {"post": None, "comments": []}
    
    try:
        cursor = conn.cursor()
        
        # Retrieve the post details
        cursor.execute("""
            SELECT p.id, u.name AS user_name, p.content, p.created_at
            FROM posts p
            JOIN users u ON p.user_id = u.id
            WHERE p.id = ?
        """, (post_id,))
        post = cursor.fetchone()
        
        if post:
            result["post"] = dict(post)
            
            # Retrieve all comments for the post
            cursor.execute("""
                SELECT c.comment_text, u.name AS user_name, c.created_at
                FROM comments c
                JOIN users u ON c.user_id = u.id
                WHERE c.post_id = ?
                ORDER BY c.created_at ASC
            """, (post_id,))
            
            result["comments"] = [dict(row) for row in cursor.fetchall()]
            
    except sqlite3.Error as e:
        print(f"Error retrieving post and comments: {e}")
        return None
    finally:
        if conn: conn.close()
        
    return result

# --- Example Usage ---

if __name__ == '__main__':
    # 1. Setup the database (creates tables if they don't exist)
    setup_database()
    
    # 2. Add mock users for testing
    user1_email = "alice@example.com"
    user2_email = "bob@example.com"
    add_mock_user(user1_email, name="Alice Johnson")
    add_mock_user(user2_email, name="Bob Smith")
    
    # 3. Alice creates a post
    post_content = "Just finished setting up the database schema! Feeling accomplished."
    new_post_id = add_mock_post(user1_email, post_content)
    
    if new_post_id:
        print(f"\n--- Post created with ID: {new_post_id} ---")
        
        # 4. Bob comments on Alice's post (Implementing the feature)
        print("\n--- Bob is commenting on Alice's post ---")
        add_comment(new_post_id, user2_email, "Great job, Alice! The structure looks solid.")

        # 5. Alice replies to Bob's comment (another use of the feature)
        print("\n--- Alice is replying to the post (adding another comment) ---")
        add_comment(new_post_id, user1_email, "Thanks, Bob! I appreciate the feedback.")
        
        # 6. View the post and all comments
        print(f"\n--- Displaying Post {new_post_id} with Comments ---")
        post_data = get_post_and_comments(new_post_id)
        
        if post_data and post_data["post"]:
            post = post_data["post"]
            print(f"POST by {post['user_name']} at {post['created_at']}")
            print(f"Content: {post['content']}")
            print("-" * 20)
            print("COMMENTS:")
            if post_data["comments"]:
                for comment in post_data["comments"]:
                    print(f"  > {comment['user_name']}: {comment['comment_text']} ({comment['created_at']})")
            else:
                print("  No comments yet.")
        else:
            print("Failed to retrieve post data.")

    else:
        print("\nFailed to create a mock post. Check database connection.")
