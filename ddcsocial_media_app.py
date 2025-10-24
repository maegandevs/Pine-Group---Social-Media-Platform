import tkinter as tk
from tkinter import messagebox
import sqlite3
import hashlib
import os
import re

# --- Configuration ---
DB_NAME = 'social_media.db'
ADMIN_USER = 'admin@dcccd.edu'
# Password for admin is 'admin123'. This is hashed in the database setup for consistency.
# Use this plain text password to log in as admin: admin123

# --- Utility Functions: Password Hashing ---


def hash_password(password):
    """Hashes a password using SHA-256."""
    # Use a fixed salt for simplicity in a demo, but in production, a unique salt per user is required.
    salt = "dcccd_social_salt"
    hashed = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return hashed


def check_password(hashed_password, user_password):
    """Checks a plain text password against the stored hash."""
    salt = "dcccd_social_salt"
    return hashed_password == hashlib.sha256((user_password + salt).encode('utf-8')).hexdigest()

# --- Database Functions (Unified and Translated from 'database.py' and 'database connection .py') ---


def get_db_connection():
    """Establishes a connection to the SQLite database."""
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row  # Allows accessing columns by name
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        messagebox.showerror(
            "Database Error", "Failed to connect to the database.")
        return None


def setup_database():
    """Creates the 'users' table and adds the default admin user if it doesn't exist."""
    conn = get_db_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()
        # Create the 'users' table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            name TEXT,
            bio TEXT,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Insert default admin user if not exists (using hashed password)
        admin_password_hash = hash_password('admin123')
        try:
            cursor.execute("""
            INSERT INTO users (email, password_hash, name, role)
            VALUES (?, ?, ?, ?)
            """, (ADMIN_USER, admin_password_hash, 'Administrator', 'admin'))
            conn.commit()
            print("Default admin user created.")
        except sqlite3.IntegrityError:
            # This happens if the admin user already exists (unique constraint violation)
            pass

        conn.commit()
        print("Database and 'users' table initialized successfully.")
    except sqlite3.Error as e:
        print(f"Error during database setup: {e}")
    finally:
        if conn:
            conn.close()


def register_user_db(email, password, name):
    """Adds a new user to the database."""
    conn = get_db_connection()
    if conn is None:
        return False

    hashed_pw = hash_password(password)
    try:
        cursor = conn.cursor()
        # Initial bio is empty, role is 'user'
        cursor.execute("""
        INSERT INTO users (email, password_hash, name, bio, role)
        VALUES (?, ?, ?, ?, ?)
        """, (email, hashed_pw, name, f"New user {name}", 'user'))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        messagebox.showerror("Registration Failed",
                             "A user with this email already exists.")
        return False
    except sqlite3.Error as e:
        messagebox.showerror(
            "Database Error", f"An error occurred during registration: {e}")
        return False
    finally:
        if conn:
            conn.close()


def verify_user_credentials(email, password):
    """Verifies user email and password against the database. Returns user dict or None."""
    conn = get_db_connection()
    if conn is None:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if user and check_password(user['password_hash'], password):
            # Convert sqlite3.Row to a dictionary for easier use
            return dict(user)
        return None
    except sqlite3.Error as e:
        print(f"Error verifying credentials: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_all_users():
    """Retrieves all users from the database."""
    conn = get_db_connection()
    if conn is None:
        return []

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT email, name, role, created_at FROM users")
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Error retrieving users: {e}")
        return []
    finally:
        if conn:
            conn.close()


def get_user_data(email):
    """Retrieves a single user's data (excluding password hash)."""
    conn = get_db_connection()
    if conn is None:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, email, name, bio, role, created_at FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        return dict(user) if user else None
    except sqlite3.Error as e:
        print(f"Error retrieving user data: {e}")
        return None
    finally:
        if conn:
            conn.close()


def delete_user_db(email):
    """Deletes a user from the database by email."""
    conn = get_db_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE email = ?", (email,))
        conn.commit()
        return cursor.rowcount > 0  # Return true if at least one row was deleted
    except sqlite3.Error as e:
        print(f"Error deleting user: {e}")
        messagebox.showerror(
            "Database Error", f"An error occurred while deleting user: {e}")
        return False
    finally:
        if conn:
            conn.close()

# --- GUI Functions (Based on 'register_login.py', 'ProfilePage.py', etc.) ---


def clear_window(root):
    """Destroys all widgets in the given root window."""
    for widget in root.winfo_children():
        widget.destroy()

# Main Login Screen


def show_login_screen(root):
    clear_window(root)
    root.title("Login | Social Media Platform")

    main_frame = tk.Frame(root, padx=20, pady=20)
    main_frame.pack(expand=True)

    # Title
    tk.Label(main_frame, text="User Login", font=("Arial", 16, "bold")).grid(
        row=0, column=0, columnspan=2, pady=10)

    # Email
    tk.Label(main_frame, text="Email:").grid(
        row=1, column=0, sticky="w", pady=5)
    email_entry = tk.Entry(main_frame, width=30)
    email_entry.grid(row=1, column=1, pady=5)
    email_entry.insert(0, ADMIN_USER)  # Pre-fill for easy testing

    # Password
    tk.Label(main_frame, text="Password:").grid(
        row=2, column=0, sticky="w", pady=5)
    password_entry = tk.Entry(main_frame, width=30, show="*")
    password_entry.grid(row=2, column=1, pady=5)
    password_entry.insert(0, "admin123")  # Pre-fill for easy testing

    # Login Button
    login_button = tk.Button(main_frame, text="Login", width=20,
                             command=lambda: process_login(root, email_entry.get(), password_entry.get()))
    login_button.grid(row=3, column=0, columnspan=2, pady=10)

    # Register Button
    register_button = tk.Button(main_frame, text="Register New User", width=20,
                                command=lambda: show_registration_screen(root))
    register_button.grid(row=4, column=0, columnspan=2, pady=5)

    # Forgot Password Button
    tk.Button(main_frame, text="Forgot Password?", width=20, command=lambda: show_forgot_password_screen(
        root)).grid(row=5, column=0, columnspan=2, pady=5)


def process_login(root, email, password):
    """Handles the login process."""
    if not email or not password:
        messagebox.showerror(
            "Login Failed", "Email and password are required.")
        return

    user_data = verify_user_credentials(email, password)

    if user_data:
        messagebox.showinfo("Login Successful",
                            f"Welcome, {user_data['name']}!")

        # Determine screen based on role
        if user_data['role'] == 'admin':
            show_admin_dashboard(root, user_data['email'])
        else:
            show_user_dashboard(root, user_data['email'])
    else:
        messagebox.showerror("Login Failed", "Invalid email or password.")

# Registration Screen


def show_registration_screen(root):
    clear_window(root)
    root.title("Register New User")

    main_frame = tk.Frame(root, padx=20, pady=20)
    main_frame.pack(expand=True)

    tk.Label(main_frame, text="New User Registration", font=(
        "Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

    # Name
    tk.Label(main_frame, text="Full Name:").grid(
        row=1, column=0, sticky="w", pady=5)
    name_entry = tk.Entry(main_frame, width=30)
    name_entry.grid(row=1, column=1, pady=5)

    # Email
    tk.Label(main_frame, text="Email:").grid(
        row=2, column=0, sticky="w", pady=5)
    email_entry = tk.Entry(main_frame, width=30)
    email_entry.grid(row=2, column=1, pady=5)

    # Password
    tk.Label(main_frame, text="Password:").grid(
        row=3, column=0, sticky="w", pady=5)
    password_entry = tk.Entry(main_frame, width=30, show="*")
    password_entry.grid(row=3, column=1, pady=5)

    def process_registration():
        email = email_entry.get()
        password = password_entry.get()
        name = name_entry.get()

        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$', email):
            messagebox.showerror("Registration Failed",
                                 "Invalid email format.")
            return

        if len(password) < 6:
            messagebox.showerror("Registration Failed",
                                 "Password must be at least 6 characters.")
            return

        if register_user_db(email, password, name):
            messagebox.showinfo(
                "Success", f"User {email} registered successfully!")
            # Go back to login after successful registration
            show_login_screen(root)

    # Register Button
    tk.Button(main_frame, text="Register", width=20, command=process_registration).grid(
        row=4, column=0, columnspan=2, pady=10)

    # Back to Login Button
    tk.Button(main_frame, text="Back to Login", width=20, command=lambda: show_login_screen(
        root)).grid(row=5, column=0, columnspan=2, pady=5)


# User Dashboard
def show_user_dashboard(root, user_email):
    clear_window(root)
    root.title("User Dashboard")

    user_data = get_user_data(user_email)
    if not user_data:
        messagebox.showerror("Error", "User data not found.")
        show_login_screen(root)
        return

    main_frame = tk.Frame(root, padx=20, pady=20)
    main_frame.pack(expand=True)

    tk.Label(main_frame, text=f"Welcome, {user_data['name']}!", font=(
        "Arial", 16, "bold")).pack(pady=10)
    tk.Label(main_frame, text="This is your main dashboard.",
             font=("Arial", 12)).pack(pady=5)

    # Functionality Buttons
    tk.Button(main_frame, text="View Profile", width=30,
              command=lambda: show_user_profile(root, user_email)).pack(pady=5)

    # Edit Profile Button
    tk.Button(main_frame, text="Edit Profile", width=30,
              command=lambda: edit_user_profile(root, user_email)).pack(pady=5)

    # Button for Search student
    tk.Button(main_frame, text="Search Students", width=30,
              command=lambda: search_students(root, user_email)).pack(pady=5)

    # Placeholder for the main Social Media Home Page from the uploaded HTML file
    tk.Button(main_frame, text="Go to Social Feed (Mock)", width=30,
              command=lambda: show_home_page(user_data)).pack(pady=5)

    tk.Button(main_frame, text="Logout", width=30,
              command=lambda: show_login_screen(root)).pack(pady=15)


# ----------------------------------------------Search Students ---------------------------------------------
# ---------------------------------------------- Search Other Students ---------------------------------
def search_students(root, user_email):
    """Allows the logged-in user to search for other students by name."""
    clear_window(root)
    root.title("Search Students")

    main_frame = tk.Frame(root, padx=20, pady=20)
    main_frame.pack(expand=True)

    tk.Label(main_frame, text="Search for Students", font=(
        "Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

    # Search field
    tk.Label(main_frame, text="Enter student name:").grid(
        row=1, column=0, sticky="w", pady=5)
    search_entry = tk.Entry(main_frame, width=30)
    search_entry.grid(row=1, column=1, pady=5)

    results_frame = tk.Frame(main_frame)
    results_frame.grid(row=3, column=0, columnspan=2, pady=10)

    def perform_search():
        for widget in results_frame.winfo_children():
            widget.destroy()

        search_term = search_entry.get().strip()
        if not search_term:
            messagebox.showerror("Error", "Please enter a name to search.")
            return

        conn = get_db_connection()
        if conn is None:
            return

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name, email, bio FROM users WHERE name LIKE ? AND email != ?",
                           (f"%{search_term}%", user_email))
            results = cursor.fetchall()

            if not results:
                tk.Label(results_frame, text="No students found.",
                         fg="gray").pack()
                return

            # Display results
            for i, (name, email, bio) in enumerate(results, start=1):
                tk.Label(results_frame, text=f"{i}. {name}", font=(
                    "Arial", 12, "bold")).pack(anchor="w")
                tk.Label(results_frame, text=f"📧 {email}", fg="blue").pack(
                    anchor="w")
                if bio:
                    tk.Label(results_frame, text=f"📝 {bio}", fg="gray").pack(
                        anchor="w")
                tk.Label(results_frame, text="").pack()  # spacing

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
        finally:
            conn.close()

    # Buttons
    tk.Button(main_frame, text="Search", width=15, command=perform_search).grid(
        row=2, column=0, columnspan=2, pady=10)
    tk.Button(main_frame, text="Back to Dashboard", width=20, command=lambda: show_user_dashboard(
        root, user_email)).grid(row=4, column=0, columnspan=2, pady=5)

# ----------------------------------------------Search Students ---------------------------------------------


def show_user_profile(root, user_email):
    """Displays the user's profile information."""
    clear_window(root)
    root.title("My Profile")

    user_data = get_user_data(user_email)
    if not user_data:
        messagebox.showerror("Error", "Profile data not found.")
        show_user_dashboard(root, user_email)
        return

    main_frame = tk.Frame(root, padx=20, pady=20)
    main_frame.pack(expand=True)

    tk.Label(main_frame, text="User Profile",
             font=("Arial", 18, "bold")).pack(pady=10)

    tk.Label(
        main_frame, text=f"Name: {user_data.get('name', 'N/A')}").pack(anchor="w", pady=2)
    tk.Label(
        main_frame, text=f"Email: {user_data.get('email', 'N/A')}").pack(anchor="w", pady=2)
    tk.Label(main_frame, text=f"Role: {user_data.get('role', 'user').capitalize()}").pack(
        anchor="w", pady=2)
    tk.Label(main_frame, text="Bio:").pack(anchor="w", pady=5)

    # Bio is displayed in a Text widget to handle multi-line content
    bio_text = tk.Text(main_frame, height=5, width=40, state=tk.DISABLED)
    bio_text.insert(tk.END, user_data.get('bio', 'No bio provided.'))
    bio_text.pack(pady=5)

    # insert picture

    # Back button
    tk.Button(main_frame, text="Back to Dashboard", width=30,
              command=lambda: show_user_dashboard(root, user_email)).pack(pady=20)


# ---------------------------------------------- Edit User Profile ---------------------------------
def edit_user_profile(root, user_email):
    """Allows the user to edit their profile (name and bio)."""
    clear_window(root)
    root.title("Edit Profile")

    # Fetch user data
    user_data = get_user_data(user_email)
    if not user_data:
        messagebox.showerror("Error", "User data not found.")
        show_user_dashboard(root, user_email)
        return

    main_frame = tk.Frame(root, padx=20, pady=20)
    main_frame.pack(expand=True)

    tk.Label(main_frame, text="Edit Profile", font=("Arial", 16, "bold")).grid(
        row=0, column=0, columnspan=2, pady=10)

    # Name field
    tk.Label(main_frame, text="Full Name:").grid(
        row=1, column=0, sticky="w", pady=5)
    name_entry = tk.Entry(main_frame, width=30)
    name_entry.insert(0, user_data.get("name", ""))
    name_entry.grid(row=1, column=1, pady=5)

    # Bio field
    tk.Label(main_frame, text="Bio:").grid(row=2, column=0, sticky="w", pady=5)
    bio_text = tk.Text(main_frame, height=5, width=30)
    bio_text.insert(tk.END, user_data.get("bio", ""))
    bio_text.grid(row=2, column=1, pady=5)

    # Save changes
    def save_profile_changes():
        new_name = name_entry.get().strip()
        new_bio = bio_text.get("1.0", tk.END).strip()

        if not new_name:
            messagebox.showerror("Error", "Name cannot be empty.")
            return

        conn = get_db_connection()
        if conn is None:
            return

        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET name = ?, bio = ? WHERE email = ?", (new_name, new_bio, user_email))
            conn.commit()
            messagebox.showinfo("Success", "Profile updated successfully!")
            show_user_dashboard(root, user_email)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
        finally:
            conn.close()

    tk.Button(main_frame, text="Save Changes", width=20, command=save_profile_changes).grid(
        row=3, column=0, columnspan=2, pady=10)
    tk.Button(main_frame, text="Cancel", width=20, command=lambda: show_user_dashboard(
        root, user_email)).grid(row=4, column=0, columnspan=2, pady=5)

# ----------------------------------------------Forget Password ---------------------------------


def show_forgot_password_screen(root):
    clear_window(root)
    root.title("Forgot Password")

    main_frame = tk.Frame(root, padx=20, pady=20)
    main_frame.pack(expand=True)

    tk.Label(main_frame, text="Reset Your Password", font=(
        "Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

    # Email field
    tk.Label(main_frame, text="Enter your registered email:").grid(
        row=1, column=0, sticky="w", pady=5)
    email_entry = tk.Entry(main_frame, width=30)
    email_entry.grid(row=1, column=1, pady=5)

    # New Password
    tk.Label(main_frame, text="New Password:").grid(
        row=2, column=0, sticky="w", pady=5)
    new_pw_entry = tk.Entry(main_frame, width=30, show="*")
    new_pw_entry.grid(row=2, column=1, pady=5)

    # Confirm Password
    tk.Label(main_frame, text="Confirm Password:").grid(
        row=3, column=0, sticky="w", pady=5)
    confirm_pw_entry = tk.Entry(main_frame, width=30, show="*")
    confirm_pw_entry.grid(row=3, column=1, pady=5)

    def reset_password():
        email = email_entry.get().strip()
        new_pw = new_pw_entry.get().strip()
        confirm_pw = confirm_pw_entry.get().strip()

        if not email or not new_pw:
            messagebox.showerror("Error", "All fields are required.")
            return
        if new_pw != confirm_pw:
            messagebox.showerror("Error", "Passwords do not match.")
            return
        if len(new_pw) < 6:
            messagebox.showerror(
                "Error", "Password must be at least 6 characters.")
            return

        conn = get_db_connection()
        if conn is None:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            if not user:
                messagebox.showerror("Error", "No user found with that email.")
                return

            new_hash = hash_password(new_pw)
            cursor.execute(
                "UPDATE users SET password_hash = ? WHERE email = ?", (new_hash, email))
            conn.commit()
            messagebox.showinfo(
                "Success", "Password updated successfully! Please log in again.")
            show_login_screen(root)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
        finally:
            conn.close()

    tk.Button(main_frame, text="Reset Password", width=20,
              command=reset_password).grid(row=4, column=0, columnspan=2, pady=10)
    tk.Button(main_frame, text="Back to Login", width=20, command=lambda: show_login_screen(
        root)).grid(row=5, column=0, columnspan=2, pady=5)


# ---------------------------------------------- Forgot Password ---------------------------------
def show_home_page(user_data):
    """Mocks the social media home page (from the HTML file) as a simple Tkinter window."""
    home_page = tk.Toplevel()
    home_page.title("Social Feed Mockup")
    home_page.geometry("600x400")

    tk.Label(home_page, text="Dallas College Social Platform",
             font=("Arial", 18, "bold"), fg="#1e3a8a").pack(pady=10)
    tk.Label(home_page, text=f"Welcome to the Feed, {user_data['name']}!", font=(
        "Arial", 14)).pack(pady=5)

    post_frame = tk.Frame(home_page, padx=10, pady=10, relief=tk.RIDGE, bd=2)
    post_frame.pack(pady=10, padx=20, fill='x')
    tk.Label(post_frame, text="Example Post from Kyllie Smith:",
             font=("Arial", 10, "italic")).pack(anchor='w')
    tk.Label(post_frame, text="This is an example post to show what the layout would look like.",
             wraplength=550, justify=tk.LEFT).pack(anchor='w')

    # Input area mock
    tk.Label(home_page, text="What's on your mind?").pack(pady=5)
    tk.Entry(home_page, width=60).pack(pady=5)
    tk.Button(home_page, text="Post", command=lambda: messagebox.showinfo(
        "Post Submitted", "Your post has been submitted!")).pack(pady=5)

    tk.Button(home_page, text="Close Feed",
              command=home_page.destroy).pack(pady=15)


# Admin Dashboard
def show_admin_dashboard(root, admin_email):
    clear_window(root)
    root.title("Admin Dashboard - User Management")

    main_frame = tk.Frame(root, padx=30, pady=30)
    main_frame.pack(expand=True)

    tk.Label(main_frame, text="Admin Console", font=(
        "Arial", 20, "bold"), fg="#8b0000").pack(pady=20)
    tk.Label(main_frame, text=f"Logged in as: {admin_email}", font=(
        "Arial", 10)).pack(pady=5)

    # Functionality Buttons (from 'ProfilePage.py' and 'user_management.py')
    tk.Button(main_frame, text="View All Users", width=30,
              command=lambda: show_all_users_admin(root, admin_email)).pack(pady=5)
    # The 'Add User' functionality is covered by the main Registration screen for now.
    tk.Button(main_frame, text="Register New User", width=30,
              command=lambda: show_registration_screen(root)).pack(pady=5)

    tk.Button(main_frame, text="Logout", width=30,
              command=lambda: show_login_screen(root)).pack(pady=20)


def show_all_users_admin(root, admin_email):
    """Displays a list of all users and provides an option to delete them."""
    clear_window(root)
    root.title("Admin - Manage Users")

    users = get_all_users()

    main_frame = tk.Frame(root, padx=20, pady=20)
    main_frame.pack(expand=True, fill=tk.BOTH)

    tk.Label(main_frame, text="All Registered Users",
             font=("Arial", 16, "bold")).pack(pady=10)

    # Scrollbar and Listbox setup for user list
    list_frame = tk.Frame(main_frame)
    list_frame.pack(pady=10, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(list_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    user_listbox = tk.Listbox(list_frame, width=70,
                              height=15, yscrollcommand=scrollbar.set)
    scrollbar.config(command=user_listbox.yview)
    user_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    if users:
        for user in users:
            # Format the display string: Email | Name | Role
            display_str = f"{user['email']} | Name: {user['name']} | Role: {user['role'].capitalize()}"
            user_listbox.insert(tk.END, display_str)
    else:
        user_listbox.insert(tk.END, "No users found in the database.")

    def prompt_delete_user():
        selected_index = user_listbox.curselection()
        if not selected_index:
            messagebox.showwarning(
                "Warning", "Please select a user to delete.")
            return

        # Extract the email from the selected string
        selected_item = user_listbox.get(selected_index[0])
        target_email = selected_item.split(' | ')[0].strip()

        if target_email == admin_email:
            messagebox.showerror(
                "Error", "You cannot delete your own admin account.")
            return

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user: {target_email}?"):
            if delete_user_db(target_email):
                messagebox.showinfo(
                    "Success", f"User {target_email} has been deleted.")
                # Refresh the screen
                show_all_users_admin(root, admin_email)
            else:
                messagebox.showerror("Error", "Failed to delete user.")

    # Delete Button
    tk.Button(main_frame, text="Delete Selected User", width=30,
              fg="red", command=prompt_delete_user).pack(pady=10)

    # Back button
    tk.Button(main_frame, text="Back to Admin Dashboard", width=30,
              command=lambda: show_admin_dashboard(root, admin_email)).pack(pady=5)


# --- Main Application Execution ---

def main():
    """Initializes the database and starts the main Tkinter application."""
    # 1. Initialize the database
    setup_database()

    # 2. Setup the main window
    root = tk.Tk()
    root.geometry("450x350")
    root.resizable(False, False)

    # 3. Show the initial login screen
    show_login_screen(root)

    # 4. Start the Tkinter event loop
    root.mainloop()


# if name == "main":
main()
