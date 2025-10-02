import tkinter as tk
import re
from tkinter import messagebox

# create admin account


def admin_login(username, password):

    admin_username = "administrator"
    admin_pw = "Sup3rUs3r"

    # checking logins entered matches the logins created
    if username == admin_username and password == admin_pw:
        return True  # login correct
    else:
        return False  # login failed


# getting the user input
entered_username = username_entry.cget("text")
entered_password = pw_entry.cget("text")

# login attempt
if admin_login(entered_username, entered_password):
    messagebox("Admin login successful!")
else:
    messagebox("Incorrect admin username or password.")


# Creating the window
root = tk.Tk()
root.title("Admin_Login")
root.geometry("400x150")

# create labels and entry fields
# name label
username_label = tk.Label(root, text="Enter Admin Username: ")
username_label.grid(row=0, column=0, padx=10, pady=5, stickey="w")
username_entry = tk.Entry(root)
username_entry.grid(row=0, column=1, padx=10, pady=5)

# password label
pw_label = tk.Label(root, text="Enter Admin Password: ")
pw_label.grid(row=1, column=0, padx=10, pady=5, stickey="w")
pw_entry = tk.Entry(root)
pw_entry.grid(row=1, column=1, padx=10, pady=5)

# submit button
submit_button = tk.Button(root, text="Submit", command=admin_login)
submit_button.grid(row=2, column=0, columnspan=2, pady=10)


root.mainloop()
