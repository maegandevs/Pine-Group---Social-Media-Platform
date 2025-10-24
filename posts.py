import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
import sqlite3
from datetime import datetime

DB_FILE = "social_media_full.db"
TIME_FORMAT = "%m/%d/%Y at %H:%M"

# ------------------------- DATABASE SETUP -------------------------
def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()

    # users
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE
        );
    """)

    # posts
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

    # comments
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

    # reactions
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

# ------------------------- DB OPERATIONS -------------------------
def create_user(username, email):
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("INSERT INTO users (username, email) VALUES (?, ?)", (username, email))
        conn.commit()
        return c.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_user_by_email(email):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = c.fetchone()
    conn.close()
    return row

def get_user_by_id(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def create_post_db(user_id, content):
    ts = datetime.now().strftime(TIME_FORMAT)
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO posts (user_id, content, created_at) VALUES (?, ?, ?)", (user_id, content, ts))
    conn.commit()
    conn.close()

def update_post_db(post_id, new_text):
    updated_ts = datetime.now().strftime(TIME_FORMAT)
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE posts SET content = ?, updated_at = ? WHERE id = ?", (new_text, updated_ts, post_id))
    conn.commit()
    conn.close()

def fetch_posts():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT p.id, p.user_id, u.username, p.content, p.created_at, p.updated_at
        FROM posts p
        JOIN users u ON p.user_id = u.id
        ORDER BY p.id DESC
    """)
    rows = c.fetchall()
    conn.close()
    return rows

def add_comment_db(post_id, user_id, text):
    ts = datetime.now().strftime(TIME_FORMAT)
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO comments (post_id, user_id, comment_text, created_at) VALUES (?, ?, ?, ?)",
              (post_id, user_id, text, ts))
    conn.commit()
    conn.close()

def get_comments_for_post(post_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT c.comment_text, u.username, c.created_at
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.post_id = ?
        ORDER BY c.id ASC
    """, (post_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_reaction_counts(post_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT reaction_type, COUNT(*) as cnt
        FROM post_reactions
        WHERE post_id = ?
        GROUP BY reaction_type
    """, (post_id,))
    rows = c.fetchall()
    conn.close()
    counts = {'like': 0, 'dislike': 0}
    for r in rows:
        counts[r['reaction_type']] = r['cnt']
    return counts

def set_reaction(post_id, user_id, reaction_type):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT reaction_type FROM post_reactions WHERE post_id = ? AND user_id = ?", (post_id, user_id))
    existing = c.fetchone()
    now = datetime.now().strftime(TIME_FORMAT)
    if existing:
        if existing['reaction_type'] == reaction_type:
            c.execute("DELETE FROM post_reactions WHERE post_id = ? AND user_id = ?", (post_id, user_id))
        else:
            c.execute("UPDATE post_reactions SET reaction_type = ?, reacted_at = ? WHERE post_id = ? AND user_id = ?",
                      (reaction_type, now, post_id, user_id))
    else:
        c.execute("INSERT INTO post_reactions (post_id, user_id, reaction_type, reacted_at) VALUES (?, ?, ?, ?)",
                  (post_id, user_id, reaction_type, now))
    conn.commit()
    conn.close()

# ------------------------- GUI -------------------------
class SocialApp:
    def __init__(self, root):
        self.root = root
        root.title("Instagram-Style Posts")
        root.geometry("1000x700")
        root.config(bg="#fafafa")
        self.current_user = None

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure("TLabel", background="#fafafa")

        # LEFT PANEL
        self.left_frame = tk.Frame(root, bg="white", bd=1, relief="solid")
        self.left_frame.place(x=20, y=20, width=340, height=660)

        ttk.Label(self.left_frame, text="Account", font=("Segoe UI", 14, "bold"), background="white").pack(pady=10)

        ttk.Label(self.left_frame, text="Email", background="white").pack(anchor="w", padx=20)
        self.email_entry = ttk.Entry(self.left_frame, width=28)
        self.email_entry.pack(padx=20, pady=(0, 8))

        ttk.Label(self.left_frame, text="Username", background="white").pack(anchor="w", padx=20)
        self.username_entry = ttk.Entry(self.left_frame, width=28)
        self.username_entry.pack(padx=20, pady=(0, 8))

        btn_frame = tk.Frame(self.left_frame, bg="white")
        btn_frame.pack(pady=6)
        ttk.Button(btn_frame, text="Register", command=self.register).grid(row=0, column=0, padx=8)
        ttk.Button(btn_frame, text="Login", command=self.login).grid(row=0, column=1, padx=8)

        self.logged_label = ttk.Label(self.left_frame, text="Not logged in", background="white", font=("Segoe UI", 10))
        self.logged_label.pack(padx=20, pady=(6, 12))

        ttk.Label(self.left_frame, text="Create a Post", background="white", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=20)
        self.post_text = scrolledtext.ScrolledText(self.left_frame, width=36, height=7, wrap=tk.WORD, font=("Segoe UI", 10))
        self.post_text.pack(padx=20, pady=(6, 10))
        self.post_button = ttk.Button(self.left_frame, text="Share Post", command=self.create_post)
        self.post_button.pack(pady=6)

        # RIGHT PANEL
        self.right_frame = tk.Frame(root, bg="#fafafa", bd=0)
        self.right_frame.place(x=380, y=20, width=600, height=660)

        ttk.Label(self.right_frame, text="Feed", font=("Segoe UI", 16, "bold"), background="#fafafa").pack(pady=10)

        self.posts
