import sqlite3
import datetime
from datetime import datetime as dt
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog

DB_FILE = "social_media_full.db"
TIME_FORMAT = "%m/%d/%Y at %H:%M"

# ------------------------- DATABASE SETUP -------------------------
def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def setup_database():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE
        );
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            comment_text TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(post_id) REFERENCES posts(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS post_reactions (
            post_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            reaction_type TEXT NOT NULL CHECK(reaction_type IN ('like','dislike')),
            reacted_at TEXT NOT NULL,
            PRIMARY KEY (post_id, user_id),
            FOREIGN KEY(post_id) REFERENCES posts(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
    """)
    conn.commit()
    conn.close()
    
    
    class SocialApp:
        def __init__(self, root):
            self.root = root
            root.title("Social Media Posts")
            root.geometry("1000x700")
            root.config(bg="#fafafa")
            self.current_user = None

            style = ttk.Style()
            style.theme_use("clam")
            style.configure("TButton", font=("Segoe UI", 10), padding=6)
            style.configure("TLabel", background="#fafafa")

# -------------------------------

def is_following(follower_email, following_email):
    """Checks if the follower_email is following the following_email."""
    conn = get_conn()
    if not conn: return False

    try:
        follower_id = get_user_id_by_email(conn, follower_email)
        following_id = get_user_id_by_email(conn, following_email)

        if not follower_id or not following_id:
            return False
            
        c = conn.cursor()
        cursor.execute("""
            SELECT 1 FROM followers 
            WHERE follower_id = ? AND following_id = ?
        """, (follower_id, following_id))
        
        return cursor.fetchone() is not None
        
    except sqlite3.Error as e:
        print(f"Database error in is_following: {e}")
        return False
    finally:
        conn.close()

def follow_user(follower_email, following_email, status_label):
    """Adds a new follow relationship to the database."""
    if follower_email == following_email:
        messagebox.showerror("Error", "You cannot follow yourself!")
        return
        
    conn = get_conn()
    if not conn: 
        messagebox.showerror("Database Error", "Could not connect to database.")
        return

    try:
        follower_id = get_user_id_by_email(conn, follower_email)
        following_id = get_user_id_by_email(conn, following_email)

        if not follower_id:
            messagebox.showerror("Error", f"Follower user '{follower_email}' not found.")
            return
        if not following_id:
            messagebox.showerror("Error", f"Target user '{following_email}' not found.")
            return

        c = conn.cursor()
        # Attempt to insert the follow relationship. PRIMARY KEY constraint prevents duplicates.
        cursor.execute("""
            INSERT OR IGNORE INTO followers (follower_id, following_id) 
            VALUES (?, ?)
        """, (follower_id, following_id))
        
        conn.commit()
        
        if cursor.rowcount > 0:
            messagebox.showinfo("Success", f"You are now following {following_email}!")
        else:
            messagebox.showinfo("Info", f"You are already following {following_email}.")
            
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred while following: {e}")
    finally:
        conn.close()
        update_follow_status_ui(status_label, following_email)


def unfollow_user(follower_email, following_email, status_label):
    """Removes a follow relationship from the database."""
    conn = get_conn()
    if not conn: 
        messagebox.showerror("Database Error", "Could not connect to database.")
        return

    try:
        follower_id = get_user_id_by_email(conn, follower_email)
        following_id = get_user_id_by_email(conn, following_email)

        if not follower_id or not following_id:
            messagebox.showerror("Error", "One or both users not found.")
            return

        c = conn.cursor()
        # Delete the follow relationship
        cursor.execute("""
            DELETE FROM followers 
            WHERE follower_id = ? AND following_id = ?
        """, (follower_id, following_id))
        
        conn.commit()
        
        if cursor.rowcount > 0:
            messagebox.showinfo("Success", f"You have unfollowed {following_email}.")
        else:
            messagebox.showinfo("Info", f"You were not following {following_email}.")
            
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred while unfollowing: {e}")
    finally:
        conn.close()
        update_follow_status_ui(status_label, following_email)

def update_follow_status_ui(status_label, target_email):
    """Updates the UI label to reflect the current follow status."""
    if is_following(CURRENT_USER_EMAIL, target_email):
        status_label.config(text=f"Status: FOLLOWING {target_email}", fg="green")
    else:
        status_label.config(text=f"Status: NOT FOLLOWING {target_email}", fg="red")


def open_follow_demo_window(current_user_email):
    """Creates a demo Tkinter window to show follow/unfollow functionality."""
    demo_win = tk.Toplevel()
    demo_win.title("Follow/Unfollow Demo")
    demo_win.geometry("500x300")
    demo_win.config(bg="#f0f0f0")

    tk.Label(demo_win, text="Follow/Unfollow Another Student", font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=10)
    
    # Current User Display
    tk.Label(demo_win, text=f"Logged in as: {current_user_email}", font=("Arial", 10), fg="#333", bg="#f0f0f0").pack()
    
    # Target User Input
    tk.Label(demo_win, text="Enter Student's Email to Follow/Unfollow:", bg="#f0f0f0").pack(pady=(15, 5))
    target_email_entry = tk.Entry(demo_win, width=40, borderwidth=2, relief="groove")
    target_email_entry.insert(0, TARGET_USER_EMAIL) # Pre-fill for easy testing
    target_email_entry.pack(pady=5)
    
    # Status Label
    follow_status_label = tk.Label(demo_win, text="Status: Loading...", font=("Arial", 10, "italic"), bg="#f0f0f0")
    follow_status_label.pack(pady=10)
    
    # Button Actions
    def on_follow():
        target = target_email_entry.get()
        if target:
            follow_user(current_user_email, target, follow_status_label)
        else:
            messagebox.showerror("Input Error", "Please enter a target email.")
    
    def on_unfollow():
        target = target_email_entry.get()
        if target:
            unfollow_user(current_user_email, target, follow_status_label)
        else:
            messagebox.showerror("Input Error", "Please enter a target email.")

    # Update Status on entry change (requires tracing, simplifying with a button for this demo)
    def check_status_manual():
        target = target_email_entry.get()
        if target:
             update_follow_status_ui(follow_status_label, target)
        
    # Buttons Frame
    button_frame = tk.Frame(demo_win, bg="#f0f0f0")
    button_frame.pack(pady=20)
    
    tk.Button(button_frame, text="FOLLOW Student", command=on_follow, 
              bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), 
              width=15, relief="raised", bd=3).pack(side=tk.LEFT, padx=10)
    
    tk.Button(button_frame, text="UNFOLLOW Student", command=on_unfollow, 
              bg="#F44336", fg="white", font=("Arial", 10, "bold"), 
              width=15, relief="raised", bd=3).pack(side=tk.LEFT, padx=10)

    tk.Button(demo_win, text="Check Status", command=check_status_manual, 
              bg="#2196F3", fg="white", width=30, relief="raised", bd=3).pack(pady=10)

    # Initial status check
    update_follow_status_ui(follow_status_label, TARGET_USER_EMAIL)


if __name__ == '__main__':
    
    setup_database()
    root = tk.Tk()
    app = SocialApp(root)
    root.mainloop()