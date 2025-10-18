import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk


users = {
    "admin@dcccd.edu": {"password": "admin123", "role": "admin", "name": "Admin User", "major": "Information Technology", "bio": "System administrator for the app.",
                        "graduation_year": "N/A", "profile_picture": None, "email": "admin@dcccd.edu"},
    "user@dcccd.edu": { "password": "user123", "role": "user", "name": "John Doe", "major": "Computer Science", "bio": "Aspiring developer and tech enthusiast.",
                       "graduation_year": "2026", "profile_picture": None, "email": "user@dcccd.edu"}
}

# ------------------ Functions ------------------

def login():
    email = email_entry.get()
    password = password_entry.get()

    if email in users and users[email]["password"] == password:
        messagebox.showinfo("Login", "Login successful!")
        if users[email]["role"] == "admin":
            open_admin_dashboard(email)
        else:
            open_home_screen(email)
    else:
        messagebox.showerror("Login Failed", "Invalid email or password.")


def open_home_screen(user_email):
    user = users[user_email]
    home = tk.Toplevel(root)
    home.title("Home Screen")

    tk.Label(home, text=f"Welcome, {user['name']}!", font=("Arial", 14)).pack(pady=10)

    # Profile Picture
    if user["profile_picture"]:
        try:
            img = Image.open(user["profile_picture"])
            img = img.resize((100, 100))
            photo = ImageTk.PhotoImage(img)
            img_label = tk.Label(home, image=photo)
            img_label.image = photo
            img_label.pack(pady=5)
        except Exception:
            tk.Label(home, text="[Error loading image]").pack()

    # Display profile details
    tk.Label(home, text=f"Email: {user['email']}").pack()
    tk.Label(home, text=f"Major: {user['major']}").pack()
    tk.Label(home, text=f"Graduation Year: {user['graduation_year']}").pack()
    tk.Label(home, text=f"Bio: {user['bio']}").pack(pady=5)

    tk.Button(home, text="Edit Profile", command=lambda: edit_profile(user_email, home)).pack(pady=5)
    tk.Button(home, text="Logout", command=home.destroy).pack(pady=5)


def edit_profile(user_email, parent):
    user = users[user_email]
    edit_win = tk.Toplevel(parent)
    edit_win.title("Edit Profile")

    tk.Label(edit_win, text="Name:").pack()
    name_entry = tk.Entry(edit_win)
    name_entry.insert(0, user["name"])
    name_entry.pack()

    tk.Label(edit_win, text="Major:").pack()
    major_entry = tk.Entry(edit_win)
    major_entry.insert(0, user["major"])
    major_entry.pack()

    tk.Label(edit_win, text="Graduation Year:").pack()
    grad_entry = tk.Entry(edit_win)
    grad_entry.insert(0, user["graduation_year"])
    grad_entry.pack()

    tk.Label(edit_win, text="Bio:").pack()
    bio_entry = tk.Entry(edit_win)
    bio_entry.insert(0, user["bio"])
    bio_entry.pack()

    def upload_picture():
        file_path = filedialog.askopenfilename(
            title="Select Profile Picture",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")]
        )
        if file_path:
            user["profile_picture"] = file_path
            messagebox.showinfo("Success", "Profile picture updated!")

    tk.Button(edit_win, text="Upload Picture", command=upload_picture).pack(pady=5)

    def save_changes():
        user["name"] = name_entry.get()
        user["major"] = major_entry.get()
        user["graduation_year"] = grad_entry.get()
        user["bio"] = bio_entry.get()
        messagebox.showinfo("Success", "Profile updated successfully!")
        edit_win.destroy()

    tk.Button(edit_win, text="Save Changes", command=save_changes).pack(pady=5)


def open_admin_dashboard(admin_email):
    admin = users[admin_email]
    admin_win = tk.Toplevel(root)
    admin_win.title("Admin Dashboard")

    tk.Label(admin_win, text=f"Welcome, {admin['name']} (Administrator)", font=("Arial", 14)).pack(pady=10)

    def view_users():
        users_list = "\n".join([f"{u} ({users[u]['role']})" for u in users])
        messagebox.showinfo("Registered Users", users_list)

    def add_user():
        def save_user():
            new_email = email_entry.get().strip()
            new_password = pass_entry.get().strip()
            name = name_entry.get().strip()
            major = major_entry.get().strip()
            grad_year = grad_entry.get().strip()

            if new_email in users:
                messagebox.showerror("Error", "User already exists!")
                return

            users[new_email] = {
                "password": new_password,
                "role": "user",
                "name": name,
                "major": major,
                "bio": "New user profile.",
                "graduation_year": grad_year,
                "profile_picture": None,
                "email": new_email
            }

            messagebox.showinfo("Success", f"User {new_email} added!")
            add_win.destroy()

        add_win = tk.Toplevel(admin_win)
        add_win.title("Add User")

        tk.Label(add_win, text="Email:").pack()
        email_entry = tk.Entry(add_win)
        email_entry.pack()

        tk.Label(add_win, text="Password:").pack()
        pass_entry = tk.Entry(add_win, show="*")
        pass_entry.pack()

        tk.Label(add_win, text="Name:").pack()
        name_entry = tk.Entry(add_win)
        name_entry.pack()

        tk.Label(add_win, text="Major:").pack()
        major_entry = tk.Entry(add_win)
        major_entry.pack()

        tk.Label(add_win, text="Graduation Year:").pack()
        grad_entry = tk.Entry(add_win)
        grad_entry.pack()

        tk.Button(add_win, text="Save", command=save_user).pack(pady=5)

    def remove_user():
        def delete_user():
            target = del_entry.get().strip()
            if target in users:
                del users[target]
                messagebox.showinfo("Success", f"User {target} removed!")
            else:
                messagebox.showerror("Error", "User not found.")
            remove_win.destroy()

        remove_win = tk.Toplevel(admin_win)
        remove_win.title("Remove User")

        tk.Label(remove_win, text="Email:").pack()
        del_entry = tk.Entry(remove_win)
        del_entry.pack()

        tk.Button(remove_win, text="Remove", command=delete_user).pack(pady=5)

    tk.Button(admin_win, text="View All Users", command=view_users).pack(pady=5)
    tk.Button(admin_win, text="Add User", command=add_user).pack(pady=5)
    tk.Button(admin_win, text="Remove User", command=remove_user).pack(pady=5)
    tk.Button(admin_win, text="Logout", command=admin_win.destroy).pack(pady=5)

# ------------------ GUI Layout ------------------

root = tk.Tk()
root.title("Login System")
root.geometry("320x230")

tk.Label(root, text="Email:").pack(pady=5)
email_entry = tk.Entry(root)
email_entry.pack()

tk.Label(root, text="Password:").pack(pady=5)
password_entry = tk.Entry(root, show="*")
password_entry.pack()

tk.Button(root, text="Login", command=login).pack(pady=20)

root.mainloop()
