import email
import tkinter as tk
import re
from tkinter import *
from tkinter import messagebox
import user_management # DO NOT CHANGE

def show_(m,p,w):
   mail = m.get()
   password = p.get()
   with open("credentials.txt", "a") as f:
    f.write(mail+','+password+'\n')
    f.close()
    messagebox.showinfo("User Created",f"User : {mail} Created successfully!!!")
   w.destroy()



def new_user():
   master = Tk()
   master.geometry("400x160")
   master.title("Create New User...")
   master.resizable(False, False)

   Label(master, text="Email....").grid(row=0, column=1)
   new_email = tk.Entry(master, justify="left", width=30 ,borderwidth=3, relief="ridge")
   new_email.grid(row=1, column=1,columnspan=2)
   Label(master, text="Enter a password").grid(row=2, column=1,columnspan=2)
   new_password = (tk.Entry(master, justify="left",width=30 ,borderwidth=3, relief="ridge",show='*'))
   new_password.grid(row=3, column=1)
   b = Button(master, text='Register', command= lambda : show_(new_email,new_password,master))
   b.grid(row=4, column=1)
   Button(master, text='Cancel', command=master.destroy).grid(row=4, column=2)
   master.mainloop()

# command=lambda : btn1click()


loginCredentials = {}

#funtions
def validate(email):
       valid = not bool(re.match(r'^[a-zA-Z0-9]+@[a-zA-Z0]+\.[a-zA-Z]{3,}$', email))
       if valid:
           messagebox.showerror("Error", "Invalid email")
       return valid

def about_window():
   messagebox.showinfo("About", "Project Pine Group\n version 1.1\nsept-2025")

#---------------------------- DO NOT CHANGE --------------------------
def try_login():
    loginCredentials.clear()  # reset before loading
    
    # load all users from text file
    with open("credentials.txt", 'r') as f:
        for line in f:
            line = line.strip()
            if line:  # ignore empty lines
                email, password = line.split(",")
                loginCredentials[email.strip()] = password.strip()
    
    print("Loaded credentials:", loginCredentials)

    # get input values
    email = loginInput.get().strip()
    password = PasswordInput.get().strip()

    # check user exists
    if email in loginCredentials:
        if loginCredentials[email] == password:
            messagebox.showinfo("Login Successful", f"Welcome {email}!")
            # Open dashbard when login is successfull
            user_management.show_dashboard(root ,loginInput.get() ,loginCredentials)
        
        else:
            messagebox.showerror("Login Failed", "Wrong password")
            PasswordInput.delete(0, tk.END)
    else:
        messagebox.showerror("Login Failed", "User not found")
        loginInput.delete(0, tk.END)
# -------------------------------DO NOT CHANGE------------------------

#main window
root = Tk()
root.title("Login | Project Name")
root.geometry("400x200")
root.resizable(False, False)
mb = Menubutton ( root, text = "File")
mb.grid(row=0, column=1)
mb.menu = Menu ( mb, tearoff = 0 )
mb["menu"] = mb.menu
mb.menu.add_command(label ='Register new User', command =  new_user)
mb.menu.add_command(label ='About...', command = about_window )
mb.menu.add_separator()
mb.menu.add_command ( label = 'Exit', command = root.destroy )
mb.grid()
label = tk.Label(root, text="Login :",width=20,height=1,padx=5,pady=5)
label.grid(row=1, column=0)
label2 = tk.Label(root, text="Password :",width=20,height=1,padx=5,pady=5)
label2.grid(row=2, column=0)
loginInput = tk.Entry(root, width=20, justify="left", borderwidth=3, relief="ridge")
loginInput.grid(row=1, column=1, padx=5, pady=5)
PasswordInput = tk.Entry(root, width=20, justify="left", show="*", borderwidth=3, relief="ridge")
PasswordInput.grid(row=2, column=1, padx=5, pady=5)
btn = tk.Button(root, text="LOGIN", command=try_login,width=15,height=1,padx=3,pady=3)
btn.grid(row=6, column=0, columnspan=2)
user_management.show_login_screen(root, loginCredentials)# DO NOT CHANGE

root.mainloop()
