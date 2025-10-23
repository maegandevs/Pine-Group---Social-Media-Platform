import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
from datetime import datetime

DB_FILE = "posts.db"
TIME_FORMAT = "%m/%d/%Y at %H:%M"

# -------------------------
# Database Setup
# -------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            text TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_post(username, text, timestamp):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO posts (username, text, timestamp) VALUES (?, ?, ?)",
              (username, text, timestamp))
    conn.commit()
    conn.close()

def get_posts():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT username, text, timestamp FROM posts ORDER BY id DESC")
    posts = c.fetchall()
    conn.close()
    return posts

# -------------------------
# App Logic
# -------------------------
def create_post():
    username = username_entry.get().strip()
    content = post_text.get("1.0", tk.END).strip()

    if not username:
        messagebox.showwarning("Missing Info", "Please enter your username.")
        return
    if not content:
        messagebox.showwarning("Missing Info", "Please write something to post.")
        return

    timestamp = datetime.now().strftime(TIME_FORMAT)
    save_post(username, content, timestamp)

    post_text.delete("1.0", tk.END)
    load_posts()
    messagebox.showinfo("Posted!", "Your post was shared successfully!")

def load_posts():
    posts_frame_inner.destroy()
    create_posts_frame()

def create_posts_frame():
    global posts_frame_inner
    posts_frame_inner = tk.Frame(posts_canvas, bg="#fafafa")
    posts_canvas.create_window((0, 0), window=posts_frame_inner, anchor="nw")

    posts = get_posts()

    if not posts:
        ttk.Label(posts_frame_inner, text="No posts yet. Share your first post!",
                  background="#fafafa", font=("Segoe UI", 11, "italic")).pack(pady=20)
    else:
        for username, text, timestamp in posts:
            create_instagram_post(posts_frame_inner, username, text, timestamp)

    posts_frame_inner.update_idletasks()
    posts_canvas.config(scrollregion=posts_canvas.bbox("all"))

def create_instagram_post(parent, username, text, timestamp):
    # Instagram-style "post card"
    post_card = tk.Frame(parent, bg="white", bd=1, relief="solid")
    post_card.pack(fill="x", pady=15, padx=15)

    # Header: profile pic + username
    header_frame = tk.Frame(post_card, bg="white")
    header_frame.pack(fill="x", padx=10, pady=(10, 5))

    profile_circle = tk.Canvas(header_frame, width=40, height=40, bg="white", highlightthickness=0)
    profile_circle.create_oval(5, 5, 35, 35, fill="#d9d9d9", outline="#d9d9d9")
    profile_circle.grid(row=0, column=0, rowspan=2, padx=(5, 10))

    name_label = ttk.Label(header_frame, text=username, font=("Segoe UI", 10, "bold"))
    name_label.grid(row=0, column=1, sticky="w")

    time_label = ttk.Label(header_frame, text=timestamp, font=("Segoe UI", 8), foreground="gray")
    time_label.grid(row=1, column=1, sticky="w")

    # Fake image placeholder (like Instagram photo area)
    photo_placeholder = tk.Frame(post_card, bg="#f0f0f0", height=220)
    photo_placeholder.pack(fill="x", padx=10, pady=5)
    photo_placeholder.pack_propagate(False)

    ttk.Label(photo_placeholder, text="[ Image Placeholder ]",
              font=("Segoe UI", 10, "italic"), foreground="gray", background="#f0f0f0").pack(expand=True)

    # Caption text
    caption_frame = tk.Frame(post_card, bg="white")
    caption_frame.pack(fill="x", padx=10, pady=(5, 10))

    caption = ttk.Label(caption_frame, text=text, wraplength=360, justify="left",
                        font=("Segoe UI", 10))
    caption.pack(anchor="w")

# -------------------------
# UI Setup
# -------------------------
root = tk.Tk()
root.title("InstaText 📸")
root.geometry("900x600")
root.config(bg="#fafafa")
root.resizable(False, False)

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
style.configure("TLabel", background="#fafafa")

# Left side: post creation
left_frame = tk.Frame(root, bg="white", bd=1, relief="solid")
left_frame.place(x=20, y=20, width=350, height=560)

ttk.Label(left_frame, text="Create a Post", font=("Segoe UI", 14, "bold"),
          background="white").pack(pady=10)

ttk.Label(left_frame, text="Username:", background="white").pack(anchor="w", padx=20, pady=(10, 0))
username_entry = ttk.Entry(left_frame, width=30)
username_entry.pack(anchor="w", padx=20, pady=(0, 8))

ttk.Label(left_frame, text="Write a caption:", background="white").pack(anchor="w", padx=20)
post_text = scrolledtext.ScrolledText(left_frame, width=35, height=8, wrap=tk.WORD, font=("Segoe UI", 10))
post_text.pack(padx=20, pady=(0, 10))

post_button = ttk.Button(left_frame, text="Share Post", command=create_post)
post_button.pack(pady=10)

# Right side: posts feed
right_frame = tk.Frame(root, bg="#fafafa", bd=1, relief="solid")
right_frame.place(x=390, y=20, width=490, height=560)

ttk.Label(right_frame, text="Feed", font=("Segoe UI", 14, "bold"), background="#fafafa").pack(pady=10)

posts_canvas = tk.Canvas(right_frame, bg="#fafafa", highlightthickness=0)
scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=posts_canvas.yview)
posts_canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
posts_canvas.pack(fill="both", expand=True)

posts_frame_inner = None
create_posts_frame()

# Scroll with mouse wheel
def on_mousewheel(event):
    posts_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

posts_canvas.bind_all("<MouseWheel>", on_mousewheel)

# Init DB and load
init_db()
load_posts()

root.mainloop()
