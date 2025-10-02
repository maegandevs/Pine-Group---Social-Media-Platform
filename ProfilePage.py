import tkinter as tk
from tkinter import messagebox

# Mock database of users
users = {
    "admin@dcccd.edu": {"password": "admin123", "role": "admin"},
    "user@dcccd.edu": {"password": "user123", "role": "user"}
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


def open_home_screen(user):
    home = tk.Toplevel(root)
    home.title("Home Screen")

    tk.Label(home, text=f"Welcome, {user}!", font=("Arial", 14)).pack(pady=10)

    tk.Button(home, text="View Profile", command=lambda: messagebox.showinfo("Profile", "[Profile Page Placeholder]")).pack(pady=5)
    tk.Button(home, text="Messages", command=lambda: messagebox.showinfo("Messages", "[Messages Page Placeholder]")).pack(pady=5)
    tk.Button(home, text="Friends List", command=lambda: messagebox.showinfo("Friends List", "[Friends List Placeholder]")).pack(pady=5)
    tk.Button(home, text="Logout", command=home.destroy).pack(pady=5)


def open_admin_dashboard(admin):
    admin_win = tk.Toplevel(root)
    admin_win.title("Admin Dashboard")

    tk.Label(admin_win, text=f"Welcome, {admin} (Administrator)", font=("Arial", 14)).pack(pady=10)

    def view_users():
        users_list = "\n".join(users.keys())
        messagebox.showinfo("Registered Users", users_list)

    def add_user():
        def save_user():
            new_email = email_entry.get()
            new_password = pass_entry.get()
            users[new_email] = {"password": new_password, "role": "user"}
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

        tk.Button(add_win, text="Save", command=save_user).pack(pady=5)

    def remove_user():
        def delete_user():
            target = del_entry.get()
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
root.geometry("300x200")

tk.Label(root, text="Email:").pack(pady=5)
email_entry = tk.Entry(root)
email_entry.pack()

tk.Label(root, text="Password:").pack(pady=5)
password_entry = tk.Entry(root, show="*")
password_entry.pack()

tk.Button(root, text="Login", command=login).pack(pady=20)

root.mainloop()
