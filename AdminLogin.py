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
def process_admin_login():

    username = username_entry.get()
    password = pw_entry.get()

    # login attempt
    if admin_login(username, password):
        messagebox.showinfo(title="Successful Login",
                            message="Admin login successful!")
    else:
        messagebox.showerror(title="Login Failed",
                             message="Incorrect admin username or password.")

    # clear the entry fields after attempting to log in
    username_entry.delete(0, tk.END)
    pw_entry.delete(0, tk.END)
    username_entry.focus()


# Creating the window
root = tk.Tk()
root.title("Admin Login")
root.geometry("400x150")

# create labels and entry fields
# username label
username_label = tk.Label(root, text="Enter Admin Username: ")
username_label.grid(row=0, column=0, padx=10, pady=5, )
username_entry = tk.Entry(root)
username_entry.grid(row=0, column=1, padx=10, pady=5)

# password label
pw_label = tk.Label(root, text="Enter Admin Password: ")
pw_label.grid(row=1, column=0, padx=10, pady=5, )
pw_entry = tk.Entry(root, show="*")
pw_entry.grid(row=1, column=1, padx=10, pady=5, )

# submit button
submit_button = tk.Button(root, text="Submit", command=process_admin_login)
submit_button.grid(row=2, column=0, columnspan=2, pady=10)
root.bind("<Return>", lambda event: process_admin_login())

root.mainloop()
