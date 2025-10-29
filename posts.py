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

def create_post(user_id, content):
    ts = dt.now().strftime(TIME_FORMAT)
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO posts (user_id, content, created_at) VALUES (?, ?, ?)", (user_id, content, ts))
    post_id = c.lastrowid
    conn.commit()
    conn.close()
    return post_id

def delete_post(post_id, user_id):
    """Delete a post if it belongs to the user"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT user_id FROM posts WHERE id = ?", (post_id,))
    post = c.fetchone()
    if not post or post['user_id'] != user_id:
        conn.close()
        return False
    # Delete related data
    c.execute("DELETE FROM comments WHERE post_id = ?", (post_id,))
    c.execute("DELETE FROM post_reactions WHERE post_id = ?", (post_id,))
    c.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()
    return True

def update_post(post_id, new_text):
    updated_ts = dt.now().strftime(TIME_FORMAT)
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

# ------------------------- COMMENTS -------------------------
def add_comment(post_id, user_email, comment_text):
    if not comment_text or not post_id or not user_email:
        return False
    conn = get_conn()
    try:
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE email = ?", (user_email,))
        user_row = c.fetchone()
        if not user_row:
            return False
        user_id = user_row['id']
        c.execute("SELECT id FROM posts WHERE id = ?", (post_id,))
        if not c.fetchone():
            return False
        c.execute("INSERT INTO comments (post_id, user_id, comment_text, created_at) VALUES (?, ?, ?, ?)",
                  (post_id, user_id, comment_text, dt.now().isoformat()))
        conn.commit()
        return True
    finally:
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

# ------------------------- REACTIONS -------------------------
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
    now = dt.now().strftime(TIME_FORMAT)
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
        root.title("Social Media Posts")
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

        ttk.Label(self.left_frame, text="Account", font=("Segoe UI", 14, "bold")).pack(pady=10)
        ttk.Label(self.left_frame, text="Email").pack(anchor="w", padx=20)
        self.email_entry = ttk.Entry(self.left_frame, width=28)
        self.email_entry.pack(padx=20, pady=(0,8))

        ttk.Label(self.left_frame, text="Username").pack(anchor="w", padx=20)
        self.username_entry = ttk.Entry(self.left_frame, width=28)
        self.username_entry.pack(padx=20, pady=(0,8))

        btn_frame = tk.Frame(self.left_frame, bg="white")
        btn_frame.pack(pady=6)
        ttk.Button(btn_frame, text="Register", command=self.register).grid(row=0,column=0,padx=8)
        ttk.Button(btn_frame, text="Login", command=self.login).grid(row=0,column=1,padx=8)

        self.logged_label = ttk.Label(self.left_frame, text="Not logged in", font=("Segoe UI", 10))
        self.logged_label.pack(padx=20, pady=(6,12))

        ttk.Label(self.left_frame, text="Create a Post", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=20)
        self.post_text = scrolledtext.ScrolledText(self.left_frame, width=36, height=7, wrap=tk.WORD, font=("Segoe UI", 10))
        self.post_text.pack(padx=20, pady=(6,10))
        self.post_button = ttk.Button(self.left_frame, text="Share Post", command=self.create_post)
        self.post_button.pack(pady=6)

        # RIGHT PANEL
        self.right_frame = tk.Frame(root, bg="#fafafa", bd=0)
        self.right_frame.place(x=380, y=20, width=600, height=660)
        ttk.Label(self.right_frame, text="Feed", font=("Segoe UI", 16, "bold")).pack(pady=10)
        self.feed_frame = tk.Frame(self.right_frame, bg="#fafafa")
        self.feed_frame.pack(fill="both", expand=True)
        self.refresh_feed()

    def register(self):
        email = self.email_entry.get().strip()
        username = self.username_entry.get().strip()
        if not email or not username:
            messagebox.showwarning("Input Error", "Email and Username required")
            return
        uid = create_user(username, email)
        if uid:
            self.current_user = {'id': uid, 'username': username, 'email': email}
            self.logged_label.config(text=f"Logged in as {username}")
            messagebox.showinfo("Success", f"User {username} registered!")
            self.refresh_feed()
        else:
            messagebox.showwarning("Exists", "User already exists")

    def login(self):
        email = self.email_entry.get().strip()
        user = get_user_by_email(email)
        if user:
            self.current_user = dict(user)
            self.logged_label.config(text=f"Logged in as {user['username']}")
            messagebox.showinfo("Success", f"Welcome {user['username']}")
            self.refresh_feed()
        else:
            messagebox.showwarning("Not Found", "User not found. Please register first.")

    def create_post(self):
        if not self.current_user:
            messagebox.showwarning("Not logged in", "Please login first")
            return
        content = self.post_text.get("1.0","end").strip()
        if not content:
            messagebox.showwarning("Empty Post", "Post content cannot be empty")
            return
        create_post(self.current_user['id'], content)
        self.post_text.delete("1.0","end")
        self.refresh_feed()

    def refresh_feed(self):
        for widget in self.feed_frame.winfo_children():
            widget.destroy()
        posts = fetch_posts()
        for p in posts:
            frame = tk.Frame(self.feed_frame, bg="white", bd=1, relief="solid")
            frame.pack(fill="x", padx=10, pady=5)
            header_text = f"{p['username']} ({p['created_at']})"
            if p['updated_at']:
                header_text += "  (edited)"
            ttk.Label(frame, text=header_text, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=6, pady=2)
            ttk.Label(frame, text=p['content'], wraplength=580).pack(anchor="w", padx=6)
            # Comments
            comments = get_comments_for_post(p['id'])
            if comments:
                ttk.Label(frame, text="Comments:", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=6)
                for c in comments:
                    ttk.Label(frame, text=f"{c['username']}: {c['comment_text']}", wraplength=580, font=("Segoe UI", 9)).pack(anchor="w", padx=12)
            # Reaction counts
            counts = get_reaction_counts(p['id'])
            ttk.Label(frame, text=f"👍 {counts['like']}   👎 {counts['dislike']}", font=("Segoe UI", 9)).pack(anchor="w", padx=6)
            # Buttons
            btn_frame = tk.Frame(frame, bg="white")
            btn_frame.pack(anchor="w", pady=4, padx=6)
            ttk.Button(btn_frame, text="Like", command=lambda pid=p['id']: self.react(pid,'like')).pack(side="left", padx=2)
            ttk.Button(btn_frame, text="Dislike", command=lambda pid=p['id']: self.react(pid,'dislike')).pack(side="left", padx=2)
            ttk.Button(btn_frame, text="Comment", command=lambda pid=p['id']: self.add_comment_gui(pid)).pack(side="left", padx=2)
            if self.current_user and p['user_id'] == self.current_user['id']:
                ttk.Button(btn_frame, text="Edit", command=lambda pid=p['id']: self.edit_post_gui(pid)).pack(side="left", padx=2)
                ttk.Button(btn_frame, text="Delete", command=lambda pid=p['id']: self.delete_post_gui(pid)).pack(side="left", padx=2)

    def react(self, post_id, r_type):
        if not self.current_user:
            messagebox.showwarning("Not logged in", "Login to react")
            return
        set_reaction(post_id, self.current_user['id'], r_type)
        self.refresh_feed()

    def add_comment_gui(self, post_id):
        if not self.current_user:
            messagebox.showwarning("Not logged in", "Login to comment")
            return
        comment = simpledialog.askstring("Comment", "Enter your comment:")
        if comment:
            add_comment(post_id, self.current_user['email'], comment)
            self.refresh_feed()

    def delete_post_gui(self, post_id):
        if not self.current_user:
            messagebox.showwarning("Not logged in", "Login first")
            return
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this post?")
        if confirm:
            success = delete_post(post_id, self.current_user['id'])
            if success:
                messagebox.showinfo("Deleted", "Your post was deleted successfully.")
                self.refresh_feed()
            else:
                messagebox.showerror("Error", "You can only delete your own posts.")

    def edit_post_gui(self, post_id):
        if not self.current_user:
            messagebox.showwarning("Not logged in", "Login first")
            return
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT user_id, content FROM posts WHERE id = ?", (post_id,))
        post = c.fetchone()
        conn.close()
        if not post or post['user_id'] != self.current_user['id']:
            messagebox.showerror("Error", "You can only edit your own posts.")
            return

        # Ask for new text
        new_text = simpledialog.askstring("Edit Post", "Update your post:", initialvalue=post['content'])
        if new_text and new_text.strip():
            update_post(post_id, new_text.strip())
            messagebox.showinfo("Updated", "Post updated successfully.")
            self.refresh_feed()

# ------------------------- MAIN -------------------------
if __name__ == "__main__":
    setup_database()
    root = tk.Tk()
    app = SocialApp(root)
    root.mainloop()
